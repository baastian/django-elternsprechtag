from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from authentication.models import CustomUser, TeacherExtraData, Student, Tag
from .models import Event, Inquiry, SiteSettings, Announcements
from django.db.models import Q
from django.utils import timezone
from django.views import View

from django.urls import reverse

from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes

from .forms import BookForm, InquiryForm, cancelEventForm
from .decorators import lead_started, parent_required
from django.contrib import messages
from django.http import Http404

# Create your views here.


@login_required
@parent_required
def public_dashboard(request):
    students = request.user.students.all()

    inquiries = Inquiry.objects.filter(Q(type=0), Q(respondent=request.user))
    # create individual link for each inquiry
    custom_inquiries = []
    for inquiry in inquiries:
        custom_inquiries.append({'inquiry': inquiry, 'url': reverse(
            'inquiry_detail_view', args=[urlsafe_base64_encode(force_bytes(inquiry.id))])})

    # Hier werden alle events anhand ihres Datums aufgeteilt
    events = Event.objects.filter(Q(parent=request.user), Q(occupied=True))
    dates = []

    datetime_objects = events.values_list("start", flat=True)
    for datetime_object in datetime_objects:
        if datetime_object.date() not in dates:
            dates.append(datetime_object.date())

    events_dict = {}
    for date in dates:
        events_dict[str(date)] = events.filter(start__date=date)

    announcements = Announcements.objects.filter(
        Q(user=request.user), Q(read=False))

    return render(request, 'dashboard/public_dashboard.html', {'inquiries': custom_inquiries, "events_dict": events_dict, 'events': events, "announcements": announcements})


@ login_required
@ parent_required
def search(request):
    teachers = CustomUser.objects.filter(role=1)
    teacherExtraData = TeacherExtraData.objects.all()
    request_search = request.GET.get('q', None)
    state = 0
    if request_search is None:
        state = 0
    elif request_search.startswith('#'):
        request_search = request_search[1:]
        tags = Tag.objects.filter(Q(name__icontains=request_search) | Q(
            synonyms__icontains=request_search))  # get a list of all matching tags

        result = []
        for tag in tags:
            extraData = teacherExtraData.filter(tags=tag)

            for data in extraData:
                teacher = data.teacher
                if not teacher in result:
                    result.append(teacher)
        state = 1
    else:
        result = []
        for data in teachers.filter(last_name__icontains=request_search):
            if not data in result:
                result.append(data)
        # result = teachers.filter(last_name__icontains=request_search)
        for data in teacherExtraData.filter(acronym__icontains=request_search):
            if not data.teacher in result:
                result.append(data.teacher)
        state = 2

    custom_result = []

    for teacher in result:
        teacher_id = urlsafe_base64_encode(force_bytes(teacher.id))
        custom_result.append({'first_name': teacher.first_name,
                             'last_name': teacher.last_name, 'email': teacher.email, 'url': reverse('event_teacher_list', args=[teacher_id])})  # notwendig um den Url parameter zu dem queryset hinzu zu fügen
    # return render(request, 'dashboard/search.html', {'teachers': result, 'search': request_search})
    return render(request, 'dashboard/search.html', {'teachers': custom_result, 'state': state, 'request_search': request_search})


@ login_required
@ parent_required
# man erhält eine Liste mit allen freien Terminen des Lehrers
def bookEventTeacherList(request, teacher_id):

    try:
        teacher = CustomUser.objects.filter(role=1).get(id__exact=force_str(
            urlsafe_base64_decode(teacher_id)))  # get the teacher for the id
    except CustomUser.DoesNotExist:
        return Http404("Lehrer wurde nicht gefunden")
    except CustomUser.MultipleObjectsReturned:
        print("Error")
    else:
        events = []
        for event in Event.objects.filter(Q(teacher=teacher), Q(occupied=False)):
            events.append({'event': event, 'url': reverse(
                'book_event_per_id', args=[event.id])})
        booked_events = []
        for event in Event.objects.filter(Q(occupied=True), Q(parent=request.user)):
            booked_events.append({'event': event, 'url': reverse(
                'event_per_id', args=[event.id])})
    return render(request, 'dashboard/events/teacher.html', {'teacher': teacher, 'events': events, 'booked_events': booked_events})


@ login_required
@ parent_required
@ lead_started
def bookEvent(request, event_id):  # hier werden final die Termine dann gebucht
    try:
        event = Event.objects.get(id=event_id)
    except Event.MultipleObjectsReturned:
        print("error")
    except Event.DoesNotExist:
        return Http404("This event was not found")
    else:
        if event.occupied:
            if event.parent == request.user:
                return render(request, "dashboard/events/self_occupied.html")
            else:
                return render(request, "dashboard/events/occupied.html")
        elif request.method == 'POST':
            form = BookForm(request.POST, request=request,
                            teacher=event.teacher)
            if form.is_valid():
                students = []
                for student in form.cleaned_data['student']:
                    try:
                        model_student = Student.objects.get(
                            shield_id=student)
                    except Student.DoesNotExist:
                        Http404("Error")
                    else:
                        students.append(model_student)
                # ? validation of students needed or given through the form
                inquiry = Inquiry.objects.create(
                    type=1, event=event, requester=request.user, respondent=event.teacher, reason="")
                inquiry.students.set(students)
                inquiry.save()
                event.parent = request.user
                event.status = 2
                event.student.set(students)
                event.occupied = True
                event.save()
                messages.success(request, "Gebucht")
                return redirect('home')
        else:
            form = BookForm(request=request, teacher=event.teacher)
        return render(request, 'dashboard/events/book.html', {'event_id': event_id, 'book_form': form})


@ login_required
@ parent_required
def inquiryView(request, inquiry_id):
    try:
        inquiry = Inquiry.objects.get(Q(type=0), Q(
            id=force_str(urlsafe_base64_decode(inquiry_id))))
    except Inquiry.DoesNotExist:
        return Http404("Inquiry does not exist.")

    else:
        if inquiry.event != None:
            return render(request, "dashboard/error/inquiry_ocupied.html")
        elif request.method == 'POST':
            form = InquiryForm(request.POST,
                               request=request, selected_student=inquiry.students.first, teacher=inquiry.requester, parent=inquiry.respondent)
            if form.is_valid():
                event = form.cleaned_data['event']
                event.parent = inquiry.respondent
                students = form.cleaned_data['student']

                event.student.set(students)
                event.occupied = True
                event.save()
                messages.success(request, "Gebucht")
                return redirect('home')
        else:
            form = InquiryForm(
                request=request, selected_student=inquiry.students.first, teacher=inquiry.requester, parent=inquiry.respondent)
        return render(request, "dashboard/inquiry.html", {'reason': inquiry.reason, 'form': form})


class EventView(View):
    cancel_form = cancelEventForm

    def get(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Http404("No event")
        else:
            return render(request, "dashboard/events/view.html", {'event': event, 'cancel_form': self.cancel_form, "teacher_id": urlsafe_base64_encode(force_bytes(event.teacher.id))})

    def post(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Http404("No event")
        else:
            if 'cancel_event' in request.POST:
                cancel_form = self.cancel_form(request.POST)
                if cancel_form.is_valid():
                    message = cancel_form.cleaned_data["message"]

                    Announcements.objects.create(
                        announcement_type=1,
                        user=event.teacher,
                        message='%s %s hat einen Termin abgesagt und folgende Nachricht hinterlassen: \n %s' % (
                            request.user.first_name, request.user.last_name, message)
                    )
                    event.parent = None
                    event.status = 0
                    event.occupied = False
                    event.student.clear()
                    event.save()
                    messages.success(
                        request, "Der Termin wurde erfolgreich abgesagt")
                    return redirect("home")
            return render(request, "dashboard/events/view.html", {'event': event, 'cancel_form': self.cancel_form,  "teacher_id": urlsafe_base64_encode(force_bytes(event.teacher.id))})


@login_required
@parent_required
def markAnnouncementRead(request, announcement_id):
    try:
        announcement = Announcements.objects.get(Q(id__exact=force_str(
            urlsafe_base64_decode(announcement_id))))
    except Announcements.DoesNotExist:
        return Http404("Mitteilung nicht gefunden")
    else:
        announcement.read = True
        announcement.save()
        return redirect("home")
