from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Instance
import requests, json
from ast import literal_eval

cloudAddress = "http://192.168.42.177/";

apiEndpoints = {
	"identityAuthentication":cloudAddress+ "identity/v3/auth/tokens",
	"bootInstance": cloudAddress+"compute/v2.1/servers",
	"instanceDetails" : cloudAddress+"compute/v2.1/servers",
	"linkToInstance" : cloudAddress +"compute/v2.1/servers"#add /{vm-id}/remote-consoles
}

apiMethods = {

  "identityAuthentication" : "POST",
  "bootInstance" : "POST",
  "instanceDetails" : "GET",
  "linkToInstance" : "POST"

}

apiHeaders = {
	"content-type": "application/json"
}

flavourId = {

  "tiny" : "1",
  "ds2G" : "d3"

}

flavorSpec = {
	
	"1" : {
		"ram": "512MB",
		"cpus": "1",
		"disk": "1GB"
	},
	"d3": {
		"ram": "2GB",
		"cpus": "2",
		"disk": "10GB"
	},

}

imageId = {

  "cirros" : "eaf0041e-e63c-4261-9ebb-caa2b6f42706",
  "ubuntu" : "fc580b93-92c9-4c56-b0f3-a9a9ba4470fd",
  "lubuntu" : "fc580b93-92c9-4c56-b0f3-a9a9ba4470fd"

}

networkId = "56c0dbca-4443-4038-95ef-0df570257028"#"9b36eb7d-2cad-4fe1-9d77-8115553a9720"



def main(request):
	if 'userLogged' in request.session:
		#return render(request, 'cloud/main.html', )
		instances = Instance.objects.filter(username=request.session["userLogged"])
		headerToSend = apiHeaders.update({"X-Auth-Token": request.session["userToken"]})
		allvms = []
		data = {"os-getVNCConsole": {"type": "novnc"}}; 
		if instances == None:
			return render(request, "cloud/main.html")
		for instance in instances:
			response =  restapi(apiEndpoints["instanceDetails"]+"/"+instance.instanceId, apiMethods["instanceDetails"], {}, headerToSend)
			responseLink = restapi(apiEndpoints["linkToInstance"]+"/"+instance.instanceId +"/action", apiMethods["linkToInstance"], data, headerToSend)
			if response.status_code == 401 or responseLink.status_code==401:
  				del request.session["userLogged"]
  				del request.session["userToken"]
  				return redirect('/')
  			elif response.status_code == 500 or response.status_code == 404 or responseLink.status_code==500 or responseLink.status_code==404:
  				messages.error(request,"Some error occured!")
  				return render(request, "cloud/main.html")
			response =  response.json()
			if responseLink.status_code!=409:
				responseLink = responseLink.json()
				url = responseLink["console"]["url"]
			else:
				url = "#"
			flavorId = response["server"]["flavor"]["id"]
			print(response["server"]["status"], type(response["server"]["status"]))
			# if response["server"]["status"].encode("utf8") == "ACTVE":
			allvms.append({"id": instance.id, "name": response["server"]["name"], "uuid": instance.instanceId, "ram": flavorSpec[flavorId]["ram"], "disk": flavorSpec[flavorId]["disk"], "cpus": flavorSpec[flavorId]["cpus"],"vm_state": response["server"]["OS-EXT-STS:vm_state"] ,"status": response["server"]["status"], "task_state": response["server"]["OS-EXT-STS:task_state"], "url": url})

		data = {"allvms": allvms, "flavorSpec": flavorSpec}

		return render(request, "cloud/main.html", data)
			#return HttpResponse(response["server"]["name"])
	else:
		return redirect('/')
	 
    

def login(request):
	if request.method == "POST":
		username = request.POST.get("username")
		password = request.POST.get("password")
		data = {"auth": {"identity": {"methods": ["password"],"password": {"user": {"name": username,"domain": {"name": "Default"},"password": password}}}}}
		response =  restapi(apiEndpoints["identityAuthentication"], apiMethods["identityAuthentication"], data, apiHeaders)
		if response.status_code == 201:
			request.session["userLogged"] = username
			request.session["userToken"] = response.headers["x-subject-token"]
			return redirect('/main')
		else:
			messages.error(request, "Invalid Credentials!")
			return render(request, 'cloud/home.html', )
		# return HttpResponse(response.status_code)
		
	else:
		return HttpResponse(status=404)

def details(request):
	# data = {
	#     "remote_console": {
	#         "protocol": "vnc",
	#         "type": "novnc"
	#     }
	# }
	
	instance = Instance.objects.get(instanceId='9383832a-22a8-486a-bc8e-d89afbfce889')
	print(apiEndpoints["linkToInstance"]+"/"+instance.instanceId+"/"+"action/", apiMethods["linkToInstance"])
	headerToSend = apiHeaders.update({"X-Auth-Token": request.session["userToken"]})
	response =  restapi(apiEndpoints["linkToInstance"]+"/"+instance.instanceId+"/"+"action", apiMethods["linkToInstance"], data, headerToSend)
	return HttpResponse(response.content)


def home(request):
	if 'userLogged' not in request.session:
		return render(request, 'cloud/home.html', )
	else:
		return redirect('/main/')
		#return HttpResponse(request.session["userToken"])

def createInstance(request):
	if request.method=="POST":
		if 'userLogged' not in request.session:
			return render(request, 'cloud/home.html', )
		instanceName = request.POST.get("instanceName")
		image = request.POST.get("image")
		flavor = request.POST.get("flavor")

		data = {
	    	"server" : {
	        "name" : instanceName,
	        "imageRef" : imageId[image],
	        "key_name" : "test",#hardcoded
	        "flavorRef" : flavourId[flavor],
	        "networks" : [{
	            "uuid" : networkId
	        }],
	        "availability_zone": "nova",
	        "OS-DCF:diskConfig": "AUTO",
	        "metadata" : {
	            "My Server Name" : "Apache1"
	        },
	        "security_groups": [
	            {
	                "name": "default"
	            }
	        ]
	    	}
  		};
  		apiHeaders.update({"X-Auth-Token": request.session["userToken"]})
  		response =  restapi(apiEndpoints["bootInstance"], apiMethods["bootInstance"], data, apiHeaders)
  		print(response.status_code)
  		if response.status_code == 202:
  			response = response.json()
  			instanceId = response["server"]["id"]
  			newInstance = Instance(username=request.session["userLogged"], instanceId=instanceId)
  			newInstance.save()
  			return redirect('/main/')
  		elif response.status_code == 401:
  			del request.session["userLogged"]
  			del request.session["userToken"]
  			return redirect('/')
  		else:
  			messages.error(request, "Some error occured!")
			return redirect('/main/')
	else:
		return HttpResponse(status=404)

	
def restapi(url, method, data, headers):
	if method=="POST":
		response = requests.post(url, data=json.dumps(data), headers=apiHeaders)
		return response
	elif method=="GET":
		response = requests.get(url, headers=apiHeaders)
		return response