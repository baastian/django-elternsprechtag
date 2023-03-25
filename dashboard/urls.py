from django.urls import path
from .views import *

urlpatterns = [
    path('', public_dashboard, name='home'),
    path('search/', search, name='search'),
    path('events/teacher/<teacher_id>',
         bookEventTeacherList, name='event_teacher_list'),
    path('event/<event_id>/book',
         bookEventView.as_view(), name='book_event_per_id'),
    path('event/<event_id>/',
         EventView.as_view(), name='event_per_id'),
    path('inquiry/<inquiry_id>', InquiryView.as_view(),
         name="inquiry_detail_view"),
    path('announcement/<announcement_id>/mark_read',
         markAnnouncementRead, name="mark_annuncement_read"),
    path('impressum/', impressum, name='impressum')
]
