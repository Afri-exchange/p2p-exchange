from django.contrib.auth import login as auth_login
# from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import SignUpForm
# Create your views here.

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from accounts.models import Accounts
from django.views.generic import UpdateView


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', )
    template_name = 'jinja/my_account.html'
    success_url = reverse_lazy('my_account')

    def get_object(self):
        return self.request.user


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            Accounts.objects.create(acc_balance=3, owned_by=user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'jinja/signup.html', {'form': form})
