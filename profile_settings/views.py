from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.list import ListView
from authentication.models import Student
from django.contrib.auth.forms import PasswordChangeForm
from .forms import *
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from dashboard.decorators import parent_required
from teacher.decorators import teacher_required
from django.utils.decorators import method_decorator

parent_decorators = [login_required, parent_required]
teacher_decorators = [login_required, teacher_required]

# Create your views here.


@method_decorator(parent_decorators, name='dispatch')
class StudentsListView(ListView):
    model = Student
    template_name = "profile_settings/student_list.html"

    def get_queryset(self, *args, **kwargs):
        qs = super(StudentsListView, self).get_queryset(*args, **kwargs)
        qs = qs.filter(customuser=self.request.user)
        return qs


@method_decorator(login_required, name='dispatch')
class MyProfileView(View):
    def get(self, request):
        if request.user.role == 1:
            profile_form = changeProfileFormForTeacher(instance=request.user)
        else:
            profile_form = changeProfileFormForUsers(instance=request.user)
        return render(request, "profile_settings/my_profile.html", context={"profile_form": profile_form})

    def post(self, request):
        if request.user.role == 1:
            profile_form = changeProfileFormForTeacher(
                request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Änderungen erfolgreich vorgenommen")

        else:
            profile_form = changeProfileFormForUsers(
                request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Änderungen erfolgreich vorgenommen")

        return render(request, "profile_settings/my_profile.html", context={"profile_form": profile_form})


@method_decorator(login_required, name='dispatch')
class ChangePasswordView(View):
    def get(self, request):
        return render(request, "profile_settings/change_password.html", context={'change_password': PasswordChangeForm(request.user)})

    def post(self, request):
        change_password_form = PasswordChangeForm(
            request.user, request.POST)
        if change_password_form.is_valid():
            user = change_password_form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request, "Das Passwort wurde erfolgreich geändert.")
            return redirect("profile_my_profile")
        return render(request, "profile_settings/change_password.html", context={'change_password': change_password_form})


@method_decorator(teacher_decorators, name='dispatch')
class EditTagsView(View):
    def get(self, request):
        return render(request, "profile_settings/teacher_change_tags.html", context={'edit_tags': configureTagsFormForTeacher(initial={'tags': request.user.teacherextradata.tags.all()}), 'tags': request.user.teacherextradata.tags.all()})

    def post(self, request):
        tagConfigurationForm = configureTagsFormForTeacher(request.POST)
        if tagConfigurationForm.is_valid():
            extraData = request.user.teacherextradata
            extraData.tags.set(tagConfigurationForm.cleaned_data["tags"])
            extraData.save()

        return render(request, "profile_settings/teacher_change_tags.html", context={'edit_tags': tagConfigurationForm, 'tags': request.user.teacherextradata.tags.all()})
