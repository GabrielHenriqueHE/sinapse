from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.utils.translation import gettext_lazy as _

from apps.events.forms import EventForm
from apps.events.models import EventModel


def events(request):
    template = loader.get_template("events/index.html")
    return HttpResponse(template.render(None, request))


@login_required(login_url="landing_page")
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)

        if form.is_valid():

            event = form.save(commit=False)
            event.user = request.user
            event.status = EventModel.Status.OPEN
            event.save()

            return redirect("events_index")


    context = {"form": EventForm()}
    template = loader.get_template("events/create_event.html")
    return HttpResponse(template.render(context, request))


def event_details(request, id):
    template = loader.get_template("events/event_details.html")
    return HttpResponse(template.render(None, request))


def event_attendance_list(request, id):
    template = loader.get_template("events/event_attendance_list.html")
    return HttpResponse(template.render(None, request))
