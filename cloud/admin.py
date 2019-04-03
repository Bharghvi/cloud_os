# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Instance, App

admin.site.register(Instance)
admin.site.register(App)


# Register your models here.
