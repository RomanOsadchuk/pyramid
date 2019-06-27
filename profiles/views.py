from django.contrib.auth import login
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView

from .forms import SignUpForm
from .models import Profile
from .tokens import sign_up_token_generator


class SignUpView(FormView):
    template_name = 'profiles/signup.html'
    form_class = SignUpForm
    success_url = '/profiles/confirm/'

    def form_valid(self, form):
        user = form.create_user(generate_confirm_url=True)
        print(user.token)
        # send email
        return super().form_valid(form)


class ProfileDetail(DetailView):
    model = Profile


class TopProfilesList(ListView):
    model = Profile
    limit = 10
    ordering = '-points'
    template_name = 'profiles/profile_list_top.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('user')
        return queryset[:self.limit]


def confirm_email(request, token):
    user = sign_up_token_generator.parse_token(token)
    if user is None:
        raise PermissionDenied

    code = user.invitation_code
    if not Profile.objects.filter(invitation_code=code).exists():
        # user changed url or invitator changed code, so...
        raise PermissionDenied

    code_owner = Profile.objects.filter(invitation_code=code)[0]
    profile = Profile(user=user, parent=code_owner)
    profile.save()
    user.is_active = True
    user.save()
    login(request, user)
    return redirect(profile)


def confirm_needed(request):
    # dummy view for now
    return HttpResponse('confirm needed')
