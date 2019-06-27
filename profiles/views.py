from django.contrib.auth import login
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView

from .forms import SignInForm, SignUpForm
from .models import Profile
from .tokens import sign_up_token_generator


class SignInView(FormView):
    form_class = SignInForm
    template_name = 'profiles/form.html'
    extra_context = {'form_verb': 'Sign In'}

    def form_valid(self, form):
        login(self.request, form.user)
        return redirect(form.user.profile)


class SignUpView(FormView):
    form_class = SignUpForm
    # template_name = 'profiles/form.html'
    template_name = 'profiles/form.html'
    extra_context = {'form_verb': 'Sign Up'}
    success_url = '/profiles/confirm/'

    def form_valid(self, form):
        user = form.create_user(generate_token=True)
        print(user.token)
        # send email
        message = 'Confirmation letter sent to ' + form.cleaned_data['email']
        return TemplateResponse(self.request, 'profiles/message.html',
                                {'message': message})


class ProfileDetail(DetailView):
    model = Profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        child_profiles = Profile.objects.filter(parent=self.object)
        print(child_profiles)
        context['child_profiles'] = child_profiles
        return context


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
