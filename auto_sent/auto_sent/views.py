from django.http import HttpResponse


def index(request):
    return HttpResponse("This site is just for the Upload data from Json to database")
