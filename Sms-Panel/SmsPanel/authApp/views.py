from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import make_password

from .forms import SignupForm, EditProfileForm
from .models import Profiles

import ipgetter, datetime       # ipgetter for Getting user IP, and datetime for getting current date and time

####    Home Page     ####
@login_required
def home(request):
    return render(request, 'home.html')

####    Getting Client IP     ####
def get_client_ip(request):
    ip = ipgetter.myip()
    return ip


####    Signup form     ####
def signup(request):
    print('signup form')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profiles.emp_name=form.cleaned_data['emp_name']
            user.profiles.department=form.cleaned_data['department']
            user.profiles.designation=form.cleaned_data['designation']
            user.profiles.email = form.cleaned_data['email']
            pwd = form.cleaned_data['password1']
            user.profiles.password = make_password(pwd)
            user.profiles.created_on = datetime.date.today()
            user.profiles.created_by = form.cleaned_data['emp_name']
            user.profiles.created_time = datetime.time()
            user.profiles.created_ip = get_client_ip(request)
            user.profiles.updated_on = datetime.date.today()
            user.profiles.updated_by = form.cleaned_data['emp_name']
            user.profiles.updated_time = datetime.time()
            user.profiles.updated_ip = get_client_ip(request)
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


####    Profile Edit form     ####
@login_required
def edit_profile(request, pk):
    profile = get_object_or_404(Profiles, pk=pk)
    print('profile...',profile)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user.profiles)
        if form.is_valid():
            print('inside post method', form.clean())
            user = form.save(commit=False)
            user.refresh_from_db()  # load the profile instance created by the signal
            user.emp_name=form.cleaned_data['emp_name']
            user.department=form.cleaned_data['department']
            user.designation=form.cleaned_data['designation']
            user.email = form.cleaned_data['email']
            user.updated_on = datetime.date.today()
            user.updated_by = form.cleaned_data['emp_name']
            user.updated_time = datetime.time()
            user.updated_ip = get_client_ip(request)
            user.save()
            return redirect('home')
            # return JsonResponse({ 'message': 'Successfully edit'})
    else:
        print('else condition edit profile')
        form = EditProfileForm(instance = request.user.profiles)
    return render(request, 'edit_user.html', {'form': form})


####    Change Password      ####
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            update_session_auth_hash(request, user)  # Important!
            user.profiles.password = form.cleaned_data['new_password1']
            user.profiles.updated_on = datetime.date.today()
            user.profiles.updated_by = request.user.username
            user.profiles.updated_time = datetime.time()
            user.profiles.updated_ip = get_client_ip(request)
            user.save();
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_change.html', {
        'form': form
    })
