from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import LoginForm, UserUpdateForm, ProfileUpdateForm, UserCreateForm
from .models import UserProfile
from apps.audit.models import log_activity

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    log_activity(user, "User Login", "Authentication", f"User {username} logged in successfully.", request.META.get('REMOTE_ADDR'))
                    messages.success(request, f"Welcome back, {user.username}!")
                    return redirect('dashboard:index')
                else:
                    messages.error(request, "Account is disabled. Please contact administrator.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'authentication/login.html', {'form': form})

@login_required
def logout_view(request):
    log_activity(request.user, "User Logout", "Authentication", f"User {request.user.username} logged out.", request.META.get('REMOTE_ADDR'))
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('authentication:login')

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            log_activity(request.user, "Update Profile", "Authentication", "Updated user profile details.", request.META.get('REMOTE_ADDR'))
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('authentication:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    return render(request, 'authentication/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile
    })

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            log_activity(request.user, "Change Password", "Authentication", "Password changed successfully.", request.META.get('REMOTE_ADDR'))
            messages.success(request, "Your password was successfully updated!")
            return redirect('authentication:profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'authentication/change_password.html', {'form': form})

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        messages.info(request, f"If an account with email {email} exists, password reset instructions have been sent.")
        return redirect('authentication:login')
    return render(request, 'authentication/forgot_password.html')

@login_required
def user_list_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'Admin':
        messages.error(request, "Access denied. Admin permissions required.")
        return redirect('dashboard:index')

    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'authentication/user_list.html', {'users': users})

@login_required
def user_create_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'Admin':
        messages.error(request, "Access denied. Admin permissions required.")
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            role = form.cleaned_data['role']
            UserProfile.objects.update_or_create(user=user, defaults={'role': role})
            log_activity(request.user, "Create User", "Authentication", f"Created user {user.username} with role {role}.", request.META.get('REMOTE_ADDR'))
            messages.success(request, f"User {user.username} created successfully!")
            return redirect('authentication:user_list')
    else:
        form = UserCreateForm()

    return render(request, 'authentication/user_form.html', {'form': form})
