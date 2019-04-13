# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Instance(models.Model):
	username = models.CharField(max_length=100)
	instanceId = models.CharField(max_length=100)
	instanceName = models.CharField(max_length=100)
	floatingIp = models.CharField(max_length=100)

	def __str__(self):
		return self.username + ": " + self.instanceId

class App(models.Model):
	username = models.CharField(max_length=100)
	instanceId = models.CharField(max_length=100)
	appName = models.CharField(max_length=100)
	gitLink = models.CharField(max_length=100)
	branch = models.CharField(max_length=100)
	runCmd = models.CharField(max_length=100)
	appLink = models.CharField(max_length=100)
	
	def __str__(self):
		return self.username + ": " + self.appName

class Software(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(max_length=1000)
	imageName = models.CharField(max_length=100, default="default.png")
	scriptName = models.CharField(max_length=100)

	def __str__(self):
		return self.name

class SoftDependency(models.Model):
	depender = models.ForeignKey(Software, on_delete=models.CASCADE,  related_name="depender")
	dependency = models.ForeignKey(Software, on_delete = models.CASCADE,  related_name="dependency")
	order = models.IntegerField()

	def __str__(self):
		return self.depender.name+"->"+self.dependency.name

class InstalledSoftware(models.Model):
	username = models.CharField(max_length=100)
	software = models.ForeignKey(Software, on_delete=models.CASCADE, related_name="software")
	status = models.IntegerField()
	instance = models.ForeignKey(Instance, on_delete=models.CASCADE, related_name="instance")
	# 0 installed
	# 99 installing
	# else error

	def __str__(self):
		return self.username+":"+self.software.name+":"+str(self.status)

# Create your models here.
