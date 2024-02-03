from django.shortcuts import render, redirect
from django.views.generic import FormView, View
from accounts.forms import UserRegistrationForm, UserUpdateForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
# Create your views here.

class UserRegistrationView(FormView):
    template_name = 'user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user) 
        return super().form_valid(form) # ei valid function ta jate nijei nijeke call dei tai use kortechi eta.
    
class UserLoginView(LoginView):
    template_name = 'user_login.html'
    def get_success_url(self) -> str:
        return reverse_lazy('profile')
    
def Userlogout(request):
    logout(request)
    return redirect('login')
    
class UserBankAccountUpdateView(View):
    template_name = 'profile.html'

    #get: Used for displaying a form to the user with current data.
    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    #post: Used for updated data, that is submitted by the user 
    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form})

def pass_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            message = render_to_string('password_change_mail.html',{
                'user' : request.user,
            })
            to_user = request.user.email
            send_email = EmailMultiAlternatives('Password Changed', '', to=[to_user])
            send_email.attach_alternative(message, "text/html") 
            send_email.send()
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form':form, 'title':'Password Change'})

    
    
  