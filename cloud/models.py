# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Instance(models.Model):
	username = models.CharField(max_length=100)
	instanceId = models.CharField(max_length=100)

	def __str__(self):
		return self.username + ": " + self.instanceId

# Create your models here.
