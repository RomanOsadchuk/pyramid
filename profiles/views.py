from django.conf import settings
from django.contrib.auth import login, logout
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView

from .forms import SignInForm, SignUpForm
from .models import Profile
from .tokens import confirm_singup_token


class SignInView(FormView):
    form_class = SignInForm
    template_name = 'profiles/form.html'
    extra_context = {'form_verb': 'Sign In'}

    def form_valid(self, form):
        login(self.request, form.user)
        return redirect(form.user.profile)


def signout_view(request):
    logout(request)
    return redirect('signin')


# ==== Registration views ==== #

class SignUpView(FormView):
    form_class = SignUpForm
    template_name = 'profiles/form.html'
    extra_context = {'form_verb': 'Sign Up'}

    def form_valid(self, form):
        user = form.create_inactive_user(send_email=True)
        message = 'Confirmation letter sent to ' + form.cleaned_data['email']
        return TemplateResponse(self.request, 'profiles/message.html',
                                {'message': message})


def confirm_email(request, token):
    data = confirm_singup_token(token)
    if data is None:
        raise PermissionDenied
    user, code = data

    if Profile.objects.filter(invitation_code=code).exists():
        code_owner = Profile.objects.filter(invitation_code=code)[0]
    else:
        code_owner = None
        if Profile.objects.all().count() >= settings.NO_CODE_REQUIRED_COUNT:
            # bad code. create a view to reenter code and redirect there
            raise PermissionDenied

    profile = Profile(user=user, parent=code_owner)
    profile.save()
    user.is_active = True
    user.save()
    login(request, user)
    return redirect(profile)


# ==== Profile views ==== #

class ProfileDetail(DetailView):
    model = Profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        child_profiles = Profile.objects.filter(parent=self.object)
        context['child_profiles'] = child_profiles.select_related('user')
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
