from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .models import Software, SoftDependency, InstalledSoftware
import requests, json, os, threading, paramiko
from django.conf import settings

def swtemplate(request):
	if 'userLogged' in request.session:
		# file = open(os.path.join(settings.BASE_DIR, 'softScripts/myscript.sh'), encoding = 'utf-8')
		# return HttpResponse(file.read())
		softwares = Software.objects.all()
		for software in softwares:
			dependencies = SoftDependency.objects.filter(depender=software).order_by("order")
			software.dependencies = dependencies
		data = {"softwares": softwares}
		return render(request, 'cloud/swtemplate.html', data)
	else:

		return redirect('/')

def swtemplatemy(request):
	if 'userLogged' in request.session:
		softwaresSuc=InstalledSoftware.objects.filter(username=request.session["userLogged"], status=0)
		softwaresFail=InstalledSoftware.objects.filter(username=request.session["userLogged"]).exclude(status=99).exclude(status=0)
		softwaresIns=InstalledSoftware.objects.filter(username=request.session["userLogged"], status=99)
		data = {"softwares": softwaresSuc, "failed": softwaresFail, "installing": softwaresIns}
		return render(request, 'cloud/swtemplatemy.html', data)
	else:
		return redirect('/swtemplate/myapp/')

def installSoft(request, softId):
	if request.method=="POST":
		if "userLogged" not in request.session:
			redirect('/')
		software = Software.objects.get(id=softId)
		dependencies = SoftDependency.objects.filter(depender=software).order_by("order")
		toinstall=[]
		for dependency in dependencies:
			toinstall.append(dependency.dependency)
		toinstall.append(software)
		for software in toinstall:
			installedSoftware = InstalledSoftware(username=request.session["userLogged"], software=software, status=99)
			installedSoftware.save()
		t1 = threading.Thread(target=startInstallation, args=(toinstall)) 
		t1.start()

		return redirect("/swtemplate/myapp/")
	else:
		return HttpResponse(status=500)

def startInstallation(*toinstall):
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect('172.21.0.8', username='ubuntu', key_filename='cloudKeys/gogokey.pem')
	for software in toinstall:
		installedSoftware = InstalledSoftware.objects.get(software=software)
		exit_code, stdout, stderr = execCmd(client, software.scriptName)
		print(software.name, exit_code)
		if exit_code == 0:
			installedSoftware.status=0
		else:
			installedSoftware.status=exit_code
		installedSoftware.save()
	client.close()

def execCmd(client, script):
	channel = client.get_transport().open_session()
	with open(os.path.join(settings.BASE_DIR, 'softScripts/'+script),encoding = 'utf-8') as file:
		cmd =  file.read()
		channel.exec_command(cmd)
	stdout = channel.makefile().read().decode('utf-8')
	stderr = channel.makefile_stderr().read().decode('utf-8')
	exit_code = channel.recv_exit_status()
	channel.shutdown_write()
	channel.close()
	return [exit_code, stdout, stderr]

def test(request):
	t1 = threading.Thread(target=print_, args=()) 
	t1.start()
	print("***************Done!*************")
	return HttpResponse("hu hale")

def print_():
	i=0
	while (i<100000):
		i+=1
		print("hello\n")
  
def rend():
	pass