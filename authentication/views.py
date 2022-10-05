from django.shortcuts import render, redirect
from .models import Upcomming_User, CustomUser
from django.db.models import Q
from .forms import *
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext as _


def register(request, user_token, key_token):
    if user_token is None or key_token is None:
        return redirect("help_register")

    user_data = Upcomming_User.objects.filter(
        Q(user_token=user_token), Q(access_key=key_token))

    if not user_data.exists():
        return render(request, 'authentication/register/link_error.html')

    user_data = user_data.first()

    if user_data.created + timezone.timedelta(days=30) < timezone.now():
        studi = user_data.student
        user_data.delete()
        Upcomming_User.objects.create(student=studi)
        return render(request, 'authentication/register/link_deprecated.html')

    if user_data.otp_verified:
        # check if otp was set to verified in last 3 hours
        if user_data.otp_verified_date + timezone.timedelta(hours=3) > timezone.now():
            if request.GET.get('login', False) and request.user.is_authenticated:
                user = request.user
                user.students.add(user_data.student)
                user.save()
                user_data.delete()

                return redirect("home")

            if request.GET.get('register', False):
                if request.method == 'POST':
                    form = Register_Parent_Account(request.POST)
                    if form.is_valid():
                        cu = CustomUser(
                            email=form.cleaned_data['email'],
                            first_name=form.cleaned_data['first_name'],
                            last_name=form.cleaned_data['last_name'], role=0)
                        cu.set_password(form.cleaned_data['password'])
                        cu.save()
                        cu.students.add(user_data.student)
                        cu.save()
                        user_data.delete()
                        return redirect('login')#{'page': request.GET.get("page")}

                else:
                    form = Register_Parent_Account()

                return render(
                    request,
                    "authentication/register/register_parent.html",
                    {'register_parent_account': form})
            name = user_data.student
            name = str(name)
            if len(name) > 18:
                name = name[:18]
                name = name+'...'
            # view to choose between registering a new user and logging in
            return render(
                request,
                "authentication/register/register_choose.html",
                {'child_name': name, 'path': request.get_full_path()})
        else:  # otp was verified more than 3 hours ago
            # messages.warning(
            #     request, _("The validation has timed out, please reenter your pin"))
            user_data.otp_verified = False
            user_data.save()
            form = Register_OTP()
            name = user_data.student
            name = str(name)
            if len(name) > 18:
                name = name[:18]
                name = name+'...'
            return render(
                request,
                'authentication/register/register_otp.html',
                {'otp_form': form, 'child_name': name})
    else:
        if request.method == 'POST':
            form = Register_OTP(request.POST)
            if form.is_valid():
                # type muss beachtet werden (int und str)
                if str(user_data.otp) == form.cleaned_data['otp']:
                    user_data.otp_verified = True
                    user_data.otp_verified_date = timezone.now()
                    user_data.save()
                    name = user_data.student
                    name = str(name)
                    if len(name) > 18:
                        name = name[:18]
                        name = name+'...'
                    return render(
                        request,
                        "authentication/register/register_choose.html",
                        {'child_name': name, 'path': request.get_full_path()})
                    # report the error to the user

                else:
                    messages.error(request, _("The code is invalid"))

        else:
            form = Register_OTP()
        name = user_data.student
        name = str(name)
        if len(name) > 18:
            name = name[:18]
            name = name+'...'
        return render(
            request,
            'authentication/register/register_otp.html',
            {'otp_form': form, 'child_name': name})
