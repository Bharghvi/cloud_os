from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Instance
import requests, json
from ast import literal_eval

cloudAddress = "http://192.168.43.81/";

apiEndpoints = {
	"identityAuthentication":cloudAddress+ "identity/v3/auth/tokens",
	"bootInstance": cloudAddress+"compute/v2.1/servers",
	"instanceDetails" : cloudAddress+"compute/v2.1/servers"
}

apiMethods = {

  "identityAuthentication" : "POST",
  "bootInstance" : "POST",
  "instanceDetails" : "GET",
  "getInstanceUrl" : "POST"

}

apiHeaders = {
	"content-type": "application/json"
}

flavourId = {

  "tiny" : "1",
  "ds2G" : "d3"

}

imageId = {

  "cirros" : "a8f5e7a3-aded-420c-9a24-58439c1360e6",
  "ubuntu" : "d167b6c2-6ec6-438c-8c82-ab9ec288def3",
  "lubuntu" : "a80a1321-ccfb-4853-ae9f-cc03593e13c5"

}

networkId = "7a0b2616-a9be-4210-a896-a7b3fd180ea1"#"9b36eb7d-2cad-4fe1-9d77-8115553a9720"



def main(request):
	if 'userLogged' in request.session:
		#return render(request, 'cloud/main.html', )
		instances = Instance.objects.filter(username=request.session["userLogged"])
		headerToSend = apiHeaders.update({"X-Auth-Token": request.session["userToken"]})
		allvms = []
		for instance in instances:
			response =  restapi(apiEndpoints["instanceDetails"]+"/"+instance.instanceId, apiMethods["instanceDetails"], {}, headerToSend)
			response =  response.content
			response = json.loads(response)
			allvms.append({"name": response["server"]["name"], "id": instance.instanceId})
		data = {"allvms": allvms}
		return render(request, "cloud/main.html", data)
			#return HttpResponse(response["server"]["name"])
	else:
		return redirect('/')

def checkApiStatus(responseObject):
	 
    

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
  		if response.status_code == 202:
  			response = response.json()
  			instanceId = response["server"]["id"]
  			newInstance = Instance(username=request.session["userLogged"], instanceId=instanceId)
  			newInstance.save()
  			return redirect('/main/')
		#
		#newInstance.save()  		
		# messages.success("Successfully created instance. Let's hope it gets boot up:(") 
  		return HttpResponse(response.status_code)
	else:
		return HttpResponse(status=404)

	
def restapi(url, method, data, headers):
	if method=="POST":
		response = requests.post(url, data=json.dumps(data), headers=apiHeaders)
	elif method=="GET":
		response = requests.get(url, headers=apiHeaders)
		return response