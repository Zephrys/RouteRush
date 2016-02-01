from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
import time

def home(request):
    return render(request, "index.html", {})


def check(request):
	time.sleep(5)
	return render(request, "index.html",{})