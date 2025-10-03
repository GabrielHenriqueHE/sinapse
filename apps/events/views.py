from django.http import HttpResponse
from django.template import loader


def events(request):
    template = loader.get_template("events/index.html")
    return HttpResponse(template.render(None, request))


def create_event(request):
    template = loader.get_template("events/create_event.html")
    return HttpResponse(template.render(None, request))


def event_details(request, id):
    template = loader.get_template("events/event_details.html")
    return HttpResponse(template.render(None, request))


def event_attendance_list(request, id):
    template = loader.get_template("events/event_attendance_list.html")
    return HttpResponse(template.render(None, request))
