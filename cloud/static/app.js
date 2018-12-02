var cloudIp = "http://192.168.43.81/";

var urls = {

  "identityAuthentication" : cloudIp+"identity/v3/auth/tokens",
  "bootInstance" : cloudIp+"compute/v2.1/servers",
  "instanceDetails" : cloudIp+"compute/v2.1/servers",//append instance id (/id) or name(?name=)
  "getInstanceUrl" : cloudIp+"compute/v2.1/servers",//append instance id (/id) and /action

}

var methods = {

  "identityAuthentication" : "POST",
  "bootInstance" : "POST",
  "instanceDetails" : "GET",
  "getInstanceUrl" : "POST"

}

var authToken="";
var headers = {};

//network, flav and image id hardcoded as of now

var imageId = {

  "cirros" : "81984e40-624e-4610-86f0-870b380fa176",
  "ubuntu" : "1f8f6a71-589b-4adb-93c0-a49e06530198",
  "centos" : "1f8f6a71-589b-4adb-93c0-a49e06530198"

}

var flavourId = {

  "tiny" : "1",
  "ds2G" : "d3"

}

var networkId = {

  "private-net" :  [{
    "uuid" : "ee3fdab9-d701-4e72-960e-be9b268c5e3c"
  }],

}

//config ends

//method to log user in
function logUserIn(){
  var username = document.getElementById('username').value;
  var password = document.getElementById('password').value;
  console.log(username,password);
  identityAuthenticate(username, password);
  return false;
}

function launchInstance(){
  var submitBtn = document.getElementById('launch');
  submitBtn.innerHTML = "Launching...";
  submitBtn.disabled = true;
  var username = document.getElementById('username').value;
  var password = document.getElementById('password').value;
  
  identityAuthenticate(username, password);
  return false;
}

function bootInstance(){
  var instanceName = document.getElementById('instanceName').value;
  console.log(instanceName);
  var flavor = document.getElementsByName('flavor');
  for(var i=0;i<flavor.length;i++){
    if(flavor[i].checked){
      flavor = flavor[i].value;
      break;
    }
  }
  var image = document.getElementsByName('image');
  for(var i=0;i<image.length;i++){
    if(image[i].checked){
      image = image[i].value;
      break;
    }
  }

  var data = {
    "server" : {
        "name" : instanceName,
        "imageRef" : imageId[image],
        "key_name" : "keypair2",//hardcoded
        "flavorRef" : flavourId[flavor],
        "networks" : [{
            "uuid" : "ee3fdab9-d701-4e72-960e-be9b268c5e3c"//hardcoded
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

  makeApiCall(urls["bootInstance"], methods["bootInstance"], data ,headers, onBootSuccess);
}

function onBootSuccess(response, headers){
  var submitBtn = document.getElementById('launch');
  submitBtn.innerHTML = "Booting...";
  response = JSON.parse(response);
  seeIfInstanceIsActive(response["server"]["id"]);
}

var status = "";
function seeIfInstanceIsActive(instanceId){

  var myVar = setInterval(function(){ 
    makeApiCall(urls["instanceDetails"]+"/"+instanceId , methods["instanceDetails"], null, headers, instanceDetailsResponse);
    console.log(status);
    if(status == "ACTIVE" || status == "ERROR"){
      clearInterval(myVar);
      var submitBtn = document.getElementById('launch');
      if(status == "ACTIVE"){
        submitBtn.innerHTML = "Launched";
        grabUrlForInstance(instanceId);
      }
      else if(status == "ERROR"){
        submitBtn.innerHTML = "Error! Launch Again";
        submitBtn.disabled = false;
      }
    }  
  }, 2000);
}

function instanceDetailsResponse(response, headers){
  response = JSON.parse(response);
  status = response["server"]["status"];
}

function grabUrlForInstance(instanceId){

  var data = {"os-getVNCConsole": {"type": "novnc"}};
  makeApiCall(urls["getInstanceUrl"]+"/"+instanceId+"/action", methods["getInstanceUrl"], data, headers ,getInstanceUrlResponse);

}

function getInstanceUrlResponse(response, headers){

  response = JSON.parse(response);
  var resultDiv = document.getElementById('instanceUrl');
  var url = response["console"]["url"];
  console.log(url);
  resultDiv.innerHTML = "Access your instance using <a target=\"_blank\" href=\"" + url + "\">This Link</a>.";

}

function identityAuthenticate(username, password){

  var data = {
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
        }
    }
  }

  makeApiCall(urls["identityAuthentication"], methods["identityAuthentication"], data, {} ,onAuthenticationSuccessBoot);

}

function onAuthenticationSuccessBoot(response, headerAuthToken){

  authToken = headerAuthToken;
  headers = {
    "X-Auth-Token" : authToken
  }
  console.log(authToken);
  //bootInstance();

}

function makeApiCall(url, method, data, headers,onSuccessFunction){

  data = JSON.stringify(data);
  var xhr = new XMLHttpRequest();

  xhr.addEventListener("readystatechange", function () {
    if (this.readyState === 4) {
      var response = this.response;
      var headerAuthToken = xhr.getResponseHeader("X-Subject-Token");
      onSuccessFunction(response, headerAuthToken);
    }
  });
  xhr.open(method, url);
  xhr.setRequestHeader("content-type", "application/json");
  //xhr.setRequestHeader("postman-token", "50c9e25f-a48d-a64e-9f7e-c643a0e77090");
  //xhr.setRequestHeader("X-Access-Control-Expose-Header", "x-subject-token");
  for (var key in headers) {
      if (headers.hasOwnProperty(key)) {
          xhr.setRequestHeader(key,headers[key]);
      }
  }
  xhr.send(data);

}