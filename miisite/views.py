from django.shortcuts import render,redirect
from django.http import HttpResponse, StreamingHttpResponse
from django.core.paginator import Paginator


# from miiworker.models import FileInfo, Node


def hello(request):
    return render(request, 'view.html')

def start(request):
    return render(request, 'view.html')

def stop(request):
    return render(request, 'view.html')

def pause(request):
    return render(request, 'view.html')

def resume(request):
    return render(request, 'view.html')
