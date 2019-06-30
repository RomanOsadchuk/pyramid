from django.contrib.auth.models import User
from django.test import TestCase

from .models import Profile


class ProfileTestCase(TestCase):

    def test_points_scoring(self):
        root_user = User.objects.create_user('root')
        root_profile = Profile.objects.create(user=root_user)
        a1_user = User.objects.create_user('a1')
        a1_profile = Profile.objects.create(user=a1_user, parent=root_profile)
        # root_profile - 1 point
        a2_user = User.objects.create_user('a2')
        a2_profile = Profile.objects.create(user=a2_user, parent=root_profile)
        # root_profile - 3 points
        a11_user = User.objects.create_user('a11')
        a11_profile = Profile.objects.create(user=a11_user, parent=a1_profile)
        # root_profile - 3 points, a1_profile - 1 point
        a12_user = User.objects.create_user('a12')
        a12_profile = Profile.objects.create(user=a12_user, parent=a1_profile)
        # root_profile - 4 points, a1_profile - 2 points
        a13_user = User.objects.create_user('a13')
        a13_profile = Profile.objects.create(user=a13_user, parent=a1_profile)
        # root_profile - 6 points, a1_profile - 3 points
        root_profile.refresh_from_db()
        a1_profile.refresh_from_db()
        self.assertEqual(root_profile.points, 6)
        self.assertEqual(a1_profile.points, 3)
