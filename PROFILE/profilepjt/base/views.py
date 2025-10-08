from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import NameEmailForm, ProfileImageForm, ProfileContactForm

@login_required
def profile_view(request):
    return render(request, 'base/profile.html')

@login_required
def profile_edit(request):
    user = request.user
    profile = user.profile

    name_form = NameEmailForm(instance=user)
    pw_form = PasswordChangeForm(user)
    image_form = ProfileImageForm(instance=profile)
    contact_form = ProfileContactForm(instance=profile)

    if request.method == 'POST':
        # which submit button was pressed?
        if 'save_name' in request.POST:
            name_form = NameEmailForm(request.POST, instance=user)
            if name_form.is_valid():
                name_form.save()
                messages.success(request, 'Name & email updated.')
                return redirect('profile')
        elif 'change_password' in request.POST:
            pw_form = PasswordChangeForm(user, request.POST)
            if pw_form.is_valid():
                u = pw_form.save()
                update_session_auth_hash(request, u)
                messages.success(request, 'Password changed.')
                return redirect('profile')
        elif 'save_image' in request.POST:
            image_form = ProfileImageForm(request.POST, request.FILES, instance=profile)
            if image_form.is_valid():
                image_form.save()
                messages.success(request, 'Profile image updated.')
                return redirect('profile')
        elif 'save_contact' in request.POST:
            contact_form = ProfileContactForm(request.POST, instance=profile)
            if contact_form.is_valid():
                contact_form.save()
                messages.success(request, 'Contact updated.')
                return redirect('profile')

    return render(request, 'base/profile_edit.html', {
        'name_form': name_form,
        'pw_form': pw_form,
        'image_form': image_form,
        'contact_form': contact_form,
    })
