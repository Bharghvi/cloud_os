from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .models import Instance, App
import requests, json
from ast import literal_eval
import base64

cloudAddress = "http://172.37.3.78";
cloudPort = "8080"

apiEndpoints = {
	"identityAuthentication":cloudAddress + ":" + cloudPort + "/identity/v3/auth/tokens",
	"bootInstance": cloudAddress + ":" + cloudPort + "/compute/v2.1/servers",
	"instanceDetails" : cloudAddress + ":" + cloudPort + "/compute/v2.1/servers",
	"linkToInstance" : cloudAddress  + ":" + cloudPort + "/compute/v2.1/servers",#add /{vm-id}/remote-consoles
	"createFloatingIp": cloudAddress+":9696/v2.0/floatingips",
	"findPortofDevice": cloudAddress+":9696/v2.0/ports?device_id=",#add instance id
	"associateFloatingIp": cloudAddress+":9696/v2.0/floatingips",#add instance id
	"grabLogs": cloudAddress+ ":"+ cloudPort +"/compute/v2.1/servers"#add /{vm-id}/action
}

apiMethods = {

  "identityAuthentication" : "POST",
  "bootInstance" : "POST",
  "instanceDetails" : "GET",
  "linkToInstance" : "POST",
  "createFloatingIp" : "POST",
  "findPortofDevice" : "GET",
  "associateFloatingIp" : "PUT",
  "grabLogs": "POST"

}

apiHeaders = {
	"content-type": "application/json"
}

flavourId = {

  "tiny" : "1",
  "ds2G" : "d3",
  "m1.small" : "2"

}

flavorSpec = {

	"1" : {
		"ram": "512MB",
		"cpus": "1",
		"disk": "1"
	},
	"d3": {
		"ram": "2GB",
		"cpus": "2",
		"disk": "10"
	},
	"2": {
			"ram": "2GB",
			"cpus": "1",
			"disk": "20"
	}

}

serverSource = {

  "cirros-server" : "ede11fe1-f1d2-4f38-88a1-738115a1ebc8",
  "fedora-server" : "d7dbd057-f4e9-405f-9eeb-e9d0cc0d0ef2",
  "ubuntu-server" : "4be973c8-811c-4e9a-8689-d596df447efa"
  # "lubuntu-gui" : "2899f9c0-0900-4072-9c19-9da1d260e27c"

}

serverSourceType = {
	
	"cirros-server" : "image",
  	"fedora-server" : "image",
  	"ubuntu-server" : "image"
  	# "lubuntu-gui" : "snapshot"

}

networkId = {

	"private": "a827593e-50ea-4a2b-89d8-b87ba1e82ce4",
	"public": "e3b0fc9c-f207-439d-9b9f-35de0ec45ceb"
}




def main(request):
	if 'userLogged' in request.session:
		#return render(request, 'cloud/main.html', )
		instances = Instance.objects.filter(username=request.session["userLogged"])
		headerToSend = apiHeaders.update({"X-Auth-Token": request.session["userToken"]})
		allvms = []
		data = {"os-getSPICEConsole": {"type": "spice-html5"}};
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
		data = {
		    "auth": {
		        "identity": {
		            "methods": [
		                "password"
		            ],
		            "password": {
		                "user": {
		                    "name": username,
		                    "domain": {
		                        "name": "Default"
		                    },
		                    "password": password
		                }
		            }
		        },
		        "scope": {
			      "project": {
			        "name": "admin",
			        "domain": { "id": "default" }
			      }
			    }
		    }
		}
		response =  restapi(apiEndpoints["identityAuthentication"], apiMethods["identityAuthentication"], data, apiHeaders)
		if response.status_code == 201:
			request.session["userLogged"] = username
			request.session["userToken"] = response.headers["x-subject-token"]
			return redirect('/deployinstance/')
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

	data = {"os-getSPICEConsole": {"type": "spice-html5"}};
	instance = Instance.objects.get(instanceId='9383832a-22a8-486a-bc8e-d89afbfce889')
	print(apiEndpoints["linkToInstance"]+"/"+instance.instanceId+"/"+"action/", apiMethods["linkToInstance"])
	headerToSend = apiHeaders.update({"X-Auth-Token": request.session["userToken"]})
	response =  restapi(apiEndpoints["linkToInstance"]+"/"+instance.instanceId+"/"+"action", apiMethods["linkToInstance"], data, headerToSend)
	return HttpResponse(response.content)


def home(request):
	if 'userLogged' not in request.session:
		return render(request, 'cloud/home.html', )
	else:
		return redirect('/deployinstance/')
		#return HttpResponse(request.session["userToken"])

def createInstance(request, instanceName, source, flavor, userData64):
	data = {
    	"server" : {
        "name" : instanceName,
        #"imageRef" : serverSource[image],
        "key_name" : "mykey",#hardcoded
        "flavorRef" : flavor,
        "networks" : [{
            "uuid" : networkId["private"]
        }],
        "block_device_mapping_v2": [{
		    "boot_index": 0,
		    "uuid": serverSource[source],
		    "source_type": serverSourceType[source],
		    "volume_size": flavorSpec[flavor]["disk"],
		    "destination_type": "volume",
		    "delete_on_termination": True}],
        "availability_zone": "nova",
        "OS-DCF:diskConfig": "AUTO",
        "metadata" : {
            "My Server Name" : "Apache1"
        },
        "security_groups": [
            {
                "name": "mysecgroup"
            }
        ],
        "user_data" : userData64
    	}
	};
	apiHeaders.update({"X-Auth-Token": request.session["userToken"]})
	response =  restapi(apiEndpoints["bootInstance"], apiMethods["bootInstance"], data, apiHeaders)
	return response

def launchInstance(request):
	if request.method=="POST":
		if 'userLogged' not in request.session:
			return render(request, 'cloud/home.html', )
		instanceName = request.POST.get("instanceName")
		source = request.POST.get("image")
		flavor = request.POST.get("flavor")
		response = createInstance(request, instanceName, source, flavourId[flavor], "")
		if response.status_code == 202:
			response = response.json()
			instanceId = response["server"]["id"]
			newInstance = Instance(username=request.session["userLogged"], instanceId=instanceId)
			newInstance.save()
			return redirect('/deployinstance/')
		elif response.status_code == 401:
			del request.session["userLogged"]
			del request.session["userToken"]
			return redirect('/')
		else:
			messages.error(request, "Some error occured!")
			return redirect('/deployinstance/')
	else:
		return HttpResponse(status=404)


def restapi(url, method, data, headers):
	if method=="POST":
		response = requests.post(url, data=json.dumps(data), headers=apiHeaders)
		return response
	elif method=="GET":
		response = requests.get(url, headers=apiHeaders)
		return response
	elif method=="PUT":
		response = requests.put(url, data=json.dumps(data), headers=apiHeaders)
		return response

def swtemplate(request):
	if 'userLogged' in request.session:
		return render(request, 'cloud/swtemplate.html', )
	else:
		return redirect('/')
		#return HttpResponse(request.session["userToken"])

#paasssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss
def deployapp(request):
	if 'userLogged' in request.session:
		apps = App.objects.filter(username=request.session["userLogged"])
		headerToSend = apiHeaders.update({"X-Auth-Token": request.session["userToken"]})
		allapps = []
		data = {"os-getSPICEConsole": {"type": "spice-html5"}};
		if apps == None:
			return render(request, "cloud/deployapp.html")
		for app in apps:
			response =  restapi(apiEndpoints["instanceDetails"]+"/"+app.instanceId, apiMethods["instanceDetails"], {}, headerToSend)
			responseLink = restapi(apiEndpoints["linkToInstance"]+"/"+app.instanceId +"/action", apiMethods["linkToInstance"], data, headerToSend)
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
			allapps.append({"id": app.id, "appName": app.appName, "instanceId": app.instanceId, "gitLink": app.gitLink, "branch": app.branch, "runCmd": app.runCmd , "appLink": app.appLink ,"vm_state": response["server"]["OS-EXT-STS:vm_state"] ,"status": response["server"]["status"], "task_state": response["server"]["OS-EXT-STS:task_state"], "url": url})
		print(allapps)
		data = {"allapps": allapps}

		return render(request, "cloud/deployapp.html", data)
	else:
		return redirect('/')

def buildAndDeploy(request):
	if request.method=="POST":
		if 'userLogged' not in request.session:
			return redirect('/')
		appName = request.POST.get('appName')
		link = request.POST.get('link')
		branch = request.POST.get('branch')
		runc = request.POST.get('runc')
		userData64 = getAppDeployUserData64(appName, link, branch, runc)
		response = createInstance(request, appName, "ubuntu-server", "d3", userData64)
		if response.status_code == 202:
			response = response.json()
			instanceId = response["server"]["id"]
			newApp = App(username=request.session["userLogged"], instanceId=instanceId, appName=appName, gitLink=link, branch=branch, runCmd=runc)
			newApp.save()
			messages.success(request, "Deployed Instance for your app! See Logs for app deployment status.")

			return redirect('/deployapp/')
		elif response.status_code == 401:
			del request.session["userLogged"]
			del request.session["userToken"]
			return redirect('/')
		else:
			messages.error(request, "Some error occured!")
			return redirect('/deployapp/')
	else:
		return HttpResponse(status=404)

def getAppDeployUserData64(appName, link, branch, runc):
	script = '''#!/bin/bash
/bin/su
curl -X POST \
  http://172.50.1.1:8090/httpclient.html \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/x-www-form-urlencoded' \
  -H 'postman-token: c9affc2c-8def-8053-626b-888e8187639b' \
  -d 'username=u15co005&mode=191&a=1549009937859&producttype=0&password=0217' || { echo "failed to log in cyberrom" >&2; exit 1; }
echo "Response received from cyberrom"

echo "Installing pip"
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py || { echo "Unable to download get-pip.py file" >&2; exit 1; }

python3 get-pip.py --user ||  { echo "failed installation of pip" >&2; exit 1; }
echo "Installing pip finished"

if [ ! -d apptodeploy ];then
	git clone '''+ link +''' -b '''+ branch +''' apptodeploy || { echo "Git clone failed" >&2; exit 1; }
	echo "Git clone completed"
fi

cd apptodeploy
python3 -m pip install -r requirements.txt --user || { echo "Requirements installation failed" >&2; exit 1; }
echo "Requirements installed"
echo "Build Success"
echo "Associate floating ip to get access to app"
echo "Starting your server on port 8080 check http://floatingIP:8080/ ..."
'''+ runc +''' || { echo "Unable to start server" >&2; exit 1; }
echo "Server started"'''
	return base64.b64encode(script.encode('ascii')).decode('ascii')

def createAndAssociatefp(request):
	if request.method=="POST":
		if 'userLogged' not in request.session:
			redirect('/')
		appId = request.POST.get("appId")
		app = App.objects.get(id=appId)
		instanceId = app.instanceId
		data = {"floatingip": {"floating_network_id": networkId["public"]}}
		headerToSend = apiHeaders.update({"X-Auth-Token": request.session["userToken"]})
		response = restapi(apiEndpoints["createFloatingIp"], apiMethods["createFloatingIp"], data, headerToSend)
		print(response.json())
		if response.status_code!=201:
			messages.error(request, "Error in creating floating ip")
			return redirect('/deployapp/')
		response = response.json()
		floatingip = response["floatingip"]["floating_ip_address"]
		floatingipId = response["floatingip"]["id"]
		print(floatingipId)
		response = restapi(apiEndpoints["findPortofDevice"]+instanceId, apiMethods["findPortofDevice"], "", headerToSend)
		if response.status_code!=200:
			messages.error(request, "Error in associating floating ip")
			return redirect('/deployapp/')
		response = response.json()
		print(response)
		portid = response["ports"][0]["id"]

		data = {"floatingip": {"port_id": portid}}
		print(apiEndpoints["associateFloatingIp"]+"/"+floatingipId, data)
		response = restapi(apiEndpoints["associateFloatingIp"]+"/"+floatingipId, apiMethods["associateFloatingIp"], data, headerToSend)
		print(response.json())
		if response.status_code!=200:
			messages.error(request, "Error in associating floating ip")
			return redirect('/deployapp/')
		app.appLink = "http://"+floatingip+":8080"
		app.save()
		messages.success(request, "Floating ip associated: "+floatingip)
		return redirect('/deployapp/')
	else:
		return HttpResponse(status=404)

def showLogs(request, instanceId):
	if 'userLogged' not in request.session:
		redirect('/')
	instanceId = {'instanceId': instanceId}
	return render(request, "cloud/showLogs.html", instanceId)

def grabLogs(request, instanceId):
	if 'userLogged' not in request.session:
		redirect('/')
	if request.method=="POST":
		data = {"os-getConsoleOutput": {"length": None}}
		headerToSend = apiHeaders.update({"X-Auth-Token": request.session["userToken"]})
		response = restapi(apiEndpoints["grabLogs"]+"/"+instanceId+"/action", apiMethods["grabLogs"], data, headerToSend)
		if response.status_code!=200:
			return HttpResponse(status=500)
		return JsonResponse(response.json(),safe=False)
	else:
		return HttpResponse(status=404)



