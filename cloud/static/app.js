console.log("Hi there");

window.onload = function(){
  console.log("cool");
  var x = document.getElementById("123");
  var os_img;
  var flavour;

  if (document.getElementById('tiny').checked) {
    flavour = document.getElementById('tiny').value; // put name of flavour
  }
  else if (document.getElementById('small').checked) {
    flavour = document.getElementById('small').value;
  }
  else if (document.getElementById('large').checked) {
    flavour = document.getElementById('large').value;
  }

  if (document.getElementById('cirros').checked) {
    os_img = document.getElementById('cirros').value; // put image id of our openstack
  }
  else if (document.getElementById('centos').checked) {
    os_img = document.getElementById('centos').value;
  }
  else if (document.getElementById('ubuntu').checked) {
    os_img = document.getElementById('ubuntu').value;
  }

  $(document).ready(function(e) {
    $('#launch').click(function(e) {
      e.preventDefault();
      $.ajax({
        type: "POST",
        url: "http://"+hostIP+":"+NOVAport+"/v2/"+tenantid+"/servers",
        headers: { 'Content-Type' : 'application/json',
                  'Accept' : 'application/json',
                 'X-OpenStack-Nova-API-Version' : '2.11',
                  'X-Auth-Token' : mytoken },
        body: json.stringify({"server": {"name": "vm1",
                                        "imageRef": "8275248f-1d55-47f7-808b-1208cfd1045d",
                                        "flavorRef": "1",
                                        "max_count": 1,
                                        "min_count": 1,
                                        "networks": [{"uuid": "02159b65-a4ad-4c9e-a087-1f3426a333ae"}],
                                        "security_groups": [{"name": "default"}]}
                            }),
        success: function(data, status, request) {
            console(request.getAllResponseHeaders();
        },
        error: function(result) {
            alert('error');
        }
    });
    })
  })
}
