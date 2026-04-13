from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import User, UserProfile
from .forms import UserRegistrationForm, UserLoginForm, ProfileForm


def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.is_verified = True  # Auto-verify users

                # Check for referral code
                referral_code = form.cleaned_data.get('referral_code')
                if referral_code:
                    try:
                        referrer = User.objects.get(referral_code=referral_code)
                        user.referred_by = referrer
                    except User.DoesNotExist:
                        pass

                user.save()

                # Create user profile
                UserProfile.objects.create(
                    user=user,
                    country=form.cleaned_data.get('country', 'Pakistan')
                )

                # Give referral bonus if applicable
                if referral_code and user.referred_by:
                    user.referred_by.balance += 1.00
                    user.referred_by.total_earned += 1.00
                    user.referred_by.save()

                    from payments.models import Transaction
                    Transaction.objects.create(
                        user=user.referred_by,
                        type='referral_bonus',
                        amount=1.00,
                        balance_after=user.referred_by.balance,
                        description=f'Referral bonus for {user.email}'
                    )

            messages.success(request, 'Account created successfully! Start earning now.')
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not email or not password:
            messages.error(request, 'Please enter both email and password.')
            return render(request, 'users/login.html', {'form': UserLoginForm()})
        
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.email}!')
            return redirect('/dashboard/')
        else:
            messages.error(request, 'Invalid email or password.')
            return render(request, 'users/login.html', {'form': UserLoginForm()})
    
    form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    """User profile"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'form': form})
