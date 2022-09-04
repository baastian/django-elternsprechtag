from django import forms
from .models import Student, TeacherStudentInquiry, SiteSettings, Event
from django.db.models import Q
from django.utils import timezone
from itertools import chain


class BookForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.teacher = kwargs.pop('teacher')
        super(BookForm, self).__init__(*args, **kwargs)

        choices = []
        if SiteSettings.objects.all().first().lead_start > timezone.now().date():  # lead not started yet
            inquiries = TeacherStudentInquiry.objects.filter(
                Q(teacher=self.teacher), Q(parent=self.request.user), Q(event=None))
            for inquiry in inquiries:
                choices.append(
                    [inquiry.student.shield_id, inquiry.student.first_name + " " + inquiry.student.last_name])  # ! shield_id can´t be exposed to the internet
        else:
            for student in self.request.user.students.all():
                choices.append(
                    [student.shield_id, student.first_name + " " + student.last_name])  # ! shield_id can´t be exposed to the internet
        self.fields['student'].choices = choices
    student = forms.MultipleChoiceField(
        choices=[], widget=forms.CheckboxSelectMultiple)


class InquiryForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.selected_student = kwargs.pop('selected_student')
        self.teacher = kwargs.pop('teacher')
        self.parent = kwargs.pop('parent')
        super(InquiryForm, self).__init__(*args, **kwargs)

        choices = []
        if SiteSettings.objects.all().first().lead_start > timezone.now().date():
            inquiries = TeacherStudentInquiry.objects.filter(
                Q(teacher=self.teacher), Q(parent=self.parent), Q(event=None))
            for inquiry in inquiries:
                choices.append(
                    [inquiry.student.shield_id, inquiry.student.first_name + " " + inquiry.student.last_name])  # ! shield_id can´t be exposed to the internet
        else:
            for student in self.request.user.students.all():
                choices.append(
                    [student.shield_id, student.first_name + " " + student.last_name])  # ! shield_id can´t be exposed to the internet
        self.fields['student'].choices = choices
        self.fields['student'].initial = [self.selected_student.shield_id,
                                          self.selected_student.first_name + " " + self.selected_student.last_name]  # ! shield_id can´t be exposed to the internet
        self.fields['event'].queryset = Event.objects.filter(
            Q(teacher=self.teacher), Q(occupied=False))

    def clean(self):
        cleaned_data = super(InquiryForm, self).clean()
        students = cleaned_data.get('student', [])
        # ! remove shield_id from being exposed to the internet
        if not self.selected_student.shield_id in students:
            self.add_error(
                'student', "The default selected student needs to stay selected")

        return cleaned_data

    event = forms.ModelChoiceField(queryset=None)
    student = forms.MultipleChoiceField(
        choices=[], widget=forms.CheckboxSelectMultiple)
