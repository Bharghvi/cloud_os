
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse


def main(request):
    return render(request, 'cloud/main.html', )

def home(request):
    return render(request, 'cloud/home.html', )
