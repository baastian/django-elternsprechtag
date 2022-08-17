from django.contrib import admin
from .models import Event, TeacherStudentInquiry

# Register your models here.


class EventAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'start', 'end', 'occupied')


admin.site.register(Event, EventAdmin)
admin.site.register(TeacherStudentInquiry)
