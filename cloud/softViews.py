from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .models import Software, SoftDependency, InstalledSoftware, Instance
import requests, json, os, threading, paramiko
from django.conf import settings
from .conf import *
from .views import restapi

def swtemplate(request):
	if 'userLogged' in request.session:
		# file = open(os.path.join(settings.BASE_DIR, 'softScripts/myscript.sh'), encoding = 'utf-8')
		# return HttpResponse(file.read())
		username=request.session["userLogged"]
		instances = Instance.objects.filter(username=username)
		softwares = Software.objects.all()
		allInstalledSoftwares={}
		allNotInstalledSoftwares={}
		for instance in instances:
			installedSoftwares = InstalledSoftware.objects.filter(username=username, instance=instance)
			softwaresYetToInstall=[]
			softwareAlreadyInstalled=[]
			for installedSoftware in installedSoftwares:
				softwareAlreadyInstalled.append(installedSoftware.software)
			for software in softwares:
				if software in softwareAlreadyInstalled:
					continue
				dependencies = SoftDependency.objects.filter(depender=software).order_by("order")
				software.dependencies = dependencies
				softwaresYetToInstall.append(software)
			allInstalledSoftwares[instance.id]=softwareAlreadyInstalled
			allNotInstalledSoftwares[instance.id]=softwaresYetToInstall

		print(allInstalledSoftwares, allNotInstalledSoftwares)
		data = {"softwares": softwares, "allInstalledSoftwares": allInstalledSoftwares, "allNotInstalledSoftwares": allNotInstalledSoftwares}
		# return HttpResponse({"1":allInstalledSoftwares, "2":allNotInstalledSoftwares})
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

def createAndAssocFloatIp(request, instance):
	instanceId = instance.instanceId
	data = {"floatingip": {"floating_network_id": networkId["public"]}}
	headerToSend = apiHeaders.update({"X-Auth-Token": request.session["userToken"]})
	response = restapi(apiEndpoints["createFloatingIp"], apiMethods["createFloatingIp"], data, headerToSend)
	if response.status_code!=201:
		return 1
	response = response.json()
	floatingip = response["floatingip"]["floating_ip_address"]
	floatingipId = response["floatingip"]["id"]
	response = restapi(apiEndpoints["findPortofDevice"]+instanceId, apiMethods["findPortofDevice"], "", headerToSend)
	if response.status_code!=200:
		return 2
	response = response.json()
	portid = response["ports"][0]["id"]

	data = {"floatingip": {"port_id": portid}}
	response = restapi(apiEndpoints["associateFloatingIp"]+"/"+floatingipId, apiMethods["associateFloatingIp"], data, headerToSend)
	if response.status_code!=200:
		return 3
	instance.floatingIp=floatingip
	instance.save()
	return 0

def installSoft(request, softId, instanceId):
	if request.method=="POST":
		if "userLogged" not in request.session:
			redirect('/')
		instance = Instance.objects.get(id=instanceId)
		resp = checkFloatingIp(instance)
		if resp == False:
			resp = createAndAssocFloatIp(request, instance)
			if resp==1:
				messages.error("Failed to create floating ip")
				return redirect("/swtemplate/newapp/")
			elif resp==2 or resp==3:
				messages.error("Failed to associate floating ip")
				return redirect("/swtemplate/newapp/")
		floatingIp = instance.floatingIp
		software = Software.objects.get(id=softId)
		dependencies = SoftDependency.objects.filter(depender=software).order_by("order")
		toinstall=[]
		for dependency in dependencies:
			installedSoftware = InstalledSoftware(username=request.session["userLogged"], software=dependency.dependency, status=99, instance=instance)
			installedSoftware.save()
			toinstall.append(installedSoftware)
		installedSoftware = InstalledSoftware(username=request.session["userLogged"], software=software, status=99, instance=instance)
		installedSoftware.save()
		toinstall.append(installedSoftware)
		# for software in toinstall:
		# 	installedSoftware = InstalledSoftware(username=request.session["userLogged"], software=software, status=99, instance=instance)
		# 	installedSoftware.save()
		t1 = threading.Thread(target=startInstallation, args=(instance, toinstall)) 
		t1.start()

		return redirect("/swtemplate/myapp/")
	else:
		return HttpResponse(status=500)

def checkFloatingIp(instance):
	if instance.floatingIp == "" :
		return False
	return True

def startInstallation(instance, *toinstall):
	toinstall=toinstall[0]
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(instance.floatingIp, username='ubuntu', key_filename='cloudKeys/'+keyName+'.pem')
	for installedSoftware in toinstall:
		# installedSoftware = InstalledSoftware.objects.get(software=software)
		exit_code, stdout, stderr = execCmd(client, installedSoftware.software.scriptName)
		print(installedSoftware.software.name, exit_code)
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