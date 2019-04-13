# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Instance, App, Software, SoftDependency, InstalledSoftware

admin.site.register(Instance)
admin.site.register(App)
admin.site.register(Software)
admin.site.register(SoftDependency)
admin.site.register(InstalledSoftware)


# Register your models here.
