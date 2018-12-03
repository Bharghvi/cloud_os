from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Instance
import requests, json

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

def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data



def main(request):
	if 'userLogged' in request.session:
		#return render(request, 'cloud/main.html', )
		instances = Instance.objects.filter(username=request.session["userLogged"])
		headerToSend = apiHeaders.update({"X-Auth-Token": request.session["userToken"]})
		allvms = []
		for instance in instances:
			response =  restapi(apiEndpoints["instanceDetails"], apiMethods["instanceDetails"], {}, headerToSend)
			#response = response.json()
			response=response.text.encode()
			# vm["name"]=response["server"]["name"]
			# allvms.append(vm)
			response = json.loads(response)
			vm["name"]=response["server"]["name"]
			allvms.append(vm)
		print(response)
		return HttpResponse(instances)
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

def home(request):
	if 'userLogged' not in request.session:
		return render(request, 'cloud/home.html', )
	else: 
		return HttpResponse(request.session["userToken"])

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
  		return HttpResponse(response)
	else:
		return HttpResponse(status=404)

	
def restapi(url, method, data, headers):
	if method=="POST":
		response = requests.post(url, data=json.dumps(data), headers=apiHeaders)
		return response
	elif method=="GET":
		response = requests.get(url, headers=apiHeaders)
		return response