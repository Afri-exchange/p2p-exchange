from django.contrib.auth import login as auth_login
# from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import SignUpForm, ProfileForm, UserForm
# Create your views here.

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from accounts.models import Accounts
from django.views.generic import UpdateView


# @method_decorator(login_required, name='dispatch')
# class UserUpdateView(UpdateView):
#     model = User
#     fields = ('first_name', 'last_name', 'email', )
#     template_name = 'jinja/my_account.html'
#     success_url = reverse_lazy('my_account')

#     def get_object(self):
#         return self.request.user


@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # messages.success(request, _(
            #     'Your profile was successfully updated!'))
            return redirect('my_account')
        # else:
        #     messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'jinja/my_account.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        form1 = ProfileForm(request.POST)
        if form.is_valid() and form1.is_valid():
            user = form.save(commit=False)
            prof = form1.save(commit=False)
            user.save()
            prof.user = user
            prof.save()
            auth_login(request, user)
            Accounts.objects.create(acc_balance=3, owned_by=user)
            return redirect('home')
    else:
        form = SignUpForm()
        form1 = ProfileForm()
    return render(request, 'jinja/signup.html', {'form': form, 'form1': form1})
