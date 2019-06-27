from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    invitation_code = models.CharField(max_length=10, blank=True, unique=True)
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username + ' profile'

    def get_absolute_url(self):
        return reverse('profile-detail', args=[str(self.id)])

    @classmethod
    def generate_code(cls):
        code = get_random_string(length=10)
        while cls.objects.filter(invitation_code=code).exists():
            code = get_random_string(length=10)
        return code

    @classmethod
    def __score_points(cls, current_profile):
        total = cls.objects.filter(parent=current_profile).count() + 1
        while total > 0:
            if not current_profile.parent:
                current_profile.points = models.F('points') + total
                current_profile.save()
                break
            current_profile.points = models.F('points') + 1
            current_profile.save()
            current_profile = current_profile.parent
            total -= 1

    def save(self, *args, **kwargs):
        if self.pk is None:  # new instance
            self.invitation_code = self.generate_code()
            if self.parent:
                self.__score_points(self.parent)
        super().save(*args, **kwargs)
