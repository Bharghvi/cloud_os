
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

  "cirros-server" : "fb3afacd-76b6-423e-bd91-0b75296b7a84",
  "fedora-server" : "51243ace-4924-4810-a269-08ad3010d2ee",
  "ubuntu-server" : "4be973c8-811c-4e9a-8689-d596df447efa",
  "lubuntu-gui" : "c27de565-6110-4bb8-a709-28c13194ee0e"

}

serverSourceType = {
	
	"cirros-server" : "image",
  	"fedora-server" : "image",
  	"ubuntu-server" : "image",
  	"lubuntu-gui" : "snapshot"

}

networkId = {

	"private": "a827593e-50ea-4a2b-89d8-b87ba1e82ce4",
	"public": "e3b0fc9c-f207-439d-9b9f-35de0ec45ceb"
}

keyName="mykey"
secGrp="mysecgroup"