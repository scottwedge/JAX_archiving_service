<!DOCTYPE html>
<html>
<head>
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta charset="utf-8">
<meta name="description" content="">
<meta name="author" content="">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="">
<!--[if lt IE 9]>
<script src="//cdnjs.cloudflare.com/ajax/libs/html5shiv/3.7.2/html5shiv.min.js"></script>
<script src="//cdnjs.cloudflare.com/ajax/libs/respond.js/1.4.2/respond.min.js"></script>
<![endif]-->
<link rel="shortcut icon" href="">
</head>
<body>

# JAX Archiving Service 

[![N|Solid](https://clic-ctsa.org/sites/default/files/styles/large/public/2019-10/jacksonLabLogo.png)](https://jacksonlaboratory.sharepoint.com/sites/ResearchIT)

# API Documentation

## Endpoints

- [`/archive`][1]
   - [metadata][metadata_link]
- [`/retrieve`][2]
- [`/get_collection`][3]
- [`/archive_failed`][4]
- [`/archive_processing`][5]
- [`/archive_success`][6]
- [`/retrieve_failed`][7]
- [`/retrieve_processing`][8]
- [`/retrieve_success`][9]

---
### /archive
[back to top][endpoints]

This endpoint will be used by the [archive frontend][frontend] or programatically by users with an `api_key` in order to deposit files into the archive (tier 3) and store metadata. This endpoint will accept a valid `POST` archiving request as described below. The successful return for this endpoint is the object id of the metadata in mongoDB. A successful return means your request was successfully submitted to pbs and further updates on the status (to the user, data services team or metadata document) of the archiving event will be directed by pbs via this archiving microservice using other endpoints.

An unsuccessful return value will be a string (starting with `ERROR:`) describing why the request was not submitted to pbs.

The body of the `POST` request must contain the following keys [`api_key`, `metadata`, `source_folder`, `service_path`]
- `api_key`
   - Value is the string representing the key
- `metadata`
   - Value is a dictionary (in python or equivalent in other language) containing some required keys. Described in more detail below [click here][metadata_link].
- `source_folder`
   - String representing the absolute path to the directory requested to be archived
- `service_path`
   - Not applicable for requests to archive `faculty` data
   - Applicable for any of the services. Presently there are only two services archiving data (single cell & microscopy)
   - The user specified path in the archive after `/archive/services/<singlecell or microscopy>/`
   - The service will generate the correct prefix with the appropriate service name `singlecell` or `microscopy`

##### `metadata`
[back to /archive][1]

A dictionary (in python or equivalent in other language) with the following required keys [`manager_user_id`, `user_id`, `project_name`, `grant_id`, `notes`, `system_groups`, `request_type`]
-   `manager_user_id` The short username of the principal investigator (PI) owning the data.
-   `user_id` The short username of the person who generated the data. In many cases this is a postdoc. It can be the PI. 
-   `project_name` The name of the project the user specifies that the data is associated with.
-   `grant_id` The grant ID associated with the data. If there is no grant ID, set this to the empty string. The service will recognize the empty string and enter “None_entered_by_user” into mongoDB.
-   `notes` Any string the user might find useful for locating these archived files at a later date.
-   *** `system_groups`*** A list in the form of an array of the HPC group(s) that will own the data and/or have permission to access the data on the cluster.
-   `request_type` A string corresponding to the type of data requesting to be archived [`faculty`, `GT`, `singlecell`, `microscopy`].

##### Flow of actions
1. object_id of mongoDB document is returned as a string
2. After request is submitted to pbs, metadata is updated with `job_id`, user receives an email notification about request being submitted to the queue.
3. When pbs starts to process the job it will use the [`/archive_processing`][5] endpoint with the `job_id`. 
   - This will notify user and update metadata.
4. When the job is completed, pbs will use the [`/archive_success`][6] endpoint with `job_id`, `sourceSize` and `archivedSize`
   - This will notify user and update metadata.

#### Example `POST` request in python
```
import requests

url = "https://ctdataservices-prod01lp/api/archiving/archive"

payload = "{
    "api_key": "KEY",
    "metadata": {
        "manager_user_id": "piusername",
        "user_id": "username",
        "project_name": "example_project",
        "grant_id": "",
        "notes": "This is a sample notes entry",
        "system_groups": [
            "jaxuser",
            "researchit"
        ],
        "request_type": "singlecell"
    },
    "source_folder": "/projects/researchit/nanozoomer_stage",
    "service_path": "some/path/user/wants"
}"
headers = {'Content-Type': 'application/json'}

response = requests.request("POST", url, headers=headers, data=payload, verify=False)

print(response.text.encode('utf8'))
print(response.json())
```
---
### /retrieve
[back to top][endpoints]

This endpoint will be used by the [archive frontend][frontend] or programatically by users with an `api_key` in order to retrieve archived (tier 3) files. This endpoint will accept a valid `POST` retrieve request as described below. The successful return will be an integer corresponding to the number of directories submitted for retrieval.

An unsuccessful return value will be a string (starting with `ERROR:`) describing why the request was not submitted to pbs.

The body of the `POST` will contain the following keys [`api_key`, `requested_dirs`]

- `api_key`
   - Value is the string representing the key
- `requested_dirs`
   - Value is a list where each item in the list is a string representation of the `object_id` for the metadata document associated with the archived directory requesting to be retrieved.

##### Flow of retrieve actions
1. integer value corresponding to the number of directories submitted for retrieval is returned.
2. After request is submitted to pbs, metadata is updated with `job_id`, user receives an email notification about request being submitted to the queue.
3. When pbs starts to process the retrieve job it will use the `retrieve_processing` endpoint with the `job_id`. 
   - This will notify user and update metadata.
4. When the retrieve job is completed, pbs will use the `retrieve_success` endpoint with `job_id`.
   - This will notify user and update metadata.

#### Example `POST` request in python
```
import requests

url = "https://ctdataservices-prod01lp.jax.org/api/archiving/retrieve"

payload = "{
		"api_key":"KEY",
		"requested_dirs":[
				"obj_id_1",
				"obj_id_2",
				"obj_id_3"
				]
	}"

headers = {'Content-Type': 'application/json'}

response = requests.request("POST", url, headers=headers, data=payload, verify=False)

print(response.text.encode('utf8'))
print(response.json())
```
---
### /get_collection 
(***To Be Redesigned***)
[back to top][endpoints]

This endpoint will accept a `GET` request as described below. The successful return will be a mongoDB collection of documents. This endpoint is primarily to be used by the [archive frontend][frontend].

This `GET` will include two args `api_key` and `gold`
- `api_key`
   - Value is the string representing the key
- `gold`
   - boolean, `true` for permanently archived metadata, `false` for operational metadata

#### example of `GET` request in python
```
import requests

url = "https://ctdataservices-prod01lp.jax.org/api/archiving/get_collection?api_key=KEY&gold=true"

payload = {}
headers= {}

response = requests.request("GET", url, headers=headers, data=payload, verify=False)

print(response.text.encode('utf8'))
print(response.json())
```
---
### /archive_failed
[back to top][endpoints]

This endpoint will accept a `GET` request as described below. This endpoint is used by internal components only to update the metadata with the the current status of `failed` and notify the data services team of the error.

The successful return will be a string with the error message generated by pbs along with the `job_id`. The metadata document associated with the `job_id` will be updated. The keys to update are `archival_status` and `when_archival_failed` with `"failed"` and `{timestamp}` respectively. The data services team will be sent an email notification about the failed job.

The unsuccessful return of this endpoint will be a string (starting with `ERROR:`) describing why the workflow of this endpoint did not fully complete successfully.

This `GET` will include two args, `api_key` and `job_id`.

- `api_key`
   - Value is a string representing the key
- `job_id`
   - Value is a string representing the `job_id` of the failed job.

#### Example `GET` request in python
```
import requests

url = "https://ctdataservices-prod01lp.jax.org/api/archiving/archive_failed?api_key=KEY&job_id=JOB_ID"

payload = {}
headers= {}

response = requests.request("GET", url, headers=headers, data=payload, verify=False)

print(response.text.encode('utf8'))
print(response.json())
```
---
### /archive_processing
[back to top][endpoints]

This endpoint will accept a `GET` request as described below. This endpoint is used by internal components only to update the metadata with the the current status of `processing`.

The successful return will be the `job_id`. The metadata document associated with the `job_id` will be updated. The keys to update are `archival_status` and `when_archival_started` with `"processing"` and `{timestamp}` respectively. The data services team will be sent an email notification about the failed job.

The unsuccessful return of this endpoint will be a string (starting with `ERROR:`) describing why the workflow of this endpoint did not fully complete successfully.

This `GET` will include two args, `api_key` and `job_id`.

- `api_key`
   - Value is a string representing the key
- `job_id`
   - Value is a string representing the `job_id` of the failed job.

#### Example `GET` request in python
```
import requests

url = "https://ctdataservices-prod01lp.jax.org/api/archiving/archive_processing?api_key=KEY&job_id=JOB_ID"

payload = {}
headers= {}

response = requests.request("GET", url, headers=headers, data=payload, verify=False)

print(response.text.encode('utf8'))
print(response.json())
```
---
### /archive_success
[back to top][endpoints]

This endpoint will accept a `GET` request as described below. This endpoint is used by internal components only to update the metadata with the the current status of `completed` and notify the user that their files were successfully deposited into the archive.

The successful return will be the `gold_document` (a python dictionary) containning the metadata. The metadata document associated with the `job_id` will be updated. The keys to update are `archival_status`, `when_archival_completed`, `sourceSize`, `archivewdSize` and `dateArchived` with `"processing"` and `{timestamp}` respectively. The user will be sent an email notification about the successfully completed job.

The unsuccessful return of this endpoint will be a string (starting with `ERROR:`) describing why the workflow of this endpoint did not fully complete successfully.

This `GET` will include four args, `api_key` and `job_id`.

- `api_key`
   - Value is a string representing the key
- `job_id`
   - Value is a string representing the `job_id` of the failed job.
- `sourceSize`
   - Integer corresponding to the original size of the archived files.
- `archivedSize`
   - Integer corresponding to the final size of the archived files.

#### Example `GET` request in python
```
import requests

url = "https://ctdataservices-prod01lp.jax.org/api/archiving/archive_success?api_key=KEY&job_id=archive.1&sourceSize=INTEGER&archivedSize=INTEGER"

payload = {}
headers= {}

response = requests.request("GET", url, headers=headers, data=payload, verify=False)

print(response.text.encode('utf8'))
print(response.json())
```
---
### /retrieve_failed
[back to top][endpoints]

This endpoint will accept a `GET` request as described below. This endpoint is used by internal components only to update the metadata with the the current status of `failed` and notify the data services team of the error.

The successful return will be a string with the error message generated by pbs along with the `job_id`. The metadata document associated with the `job_id` will be updated. The keys to update are `retrieval_status` and `when_retrieval_completed` with `"failed"` and `None` respectively. The data services team will be sent an email notification about the failed job.

The unsuccessful return of this endpoint will be a string (starting with `ERROR:`) describing why the workflow of this endpoint did not fully complete successfully.

This `GET` will include three args, `api_key`, `obj_id` and `job_id`.

- `api_key`
   - Value is a string representing the key
- `obj_id`
   - String corresponding to the object id in mongoDB for the metadata.
- `job_id`
   - Value is a string representing the `job_id` of the failed job.

#### Example `GET` request in python
```
import requests

url = "https://ctdataservices-prod01lp.jax.org/api/archiving/retrieve_failed?api_key=KEY&obj_id=OBJ_ID&job_id=JOB_ID"

payload = {}
headers= {}

response = requests.request("GET", url, headers=headers, data=payload, verify=False)

print(response.text.encode('utf8'))
print(response.json())
```
---
### /retrieve_processing
[back to top][endpoints]

This endpoint will accept a `GET` request as described below. This endpoint is used by internal components only to update the metadata with the the current status of `processing` (job started processing).

The successful return will be the `job_id`. The metadata document associated with the `job_id` will be updated. The keys to update are `retrieval_status` and `when_retrieval_started` with `"processing"` and `{timestamp}` respectively. The user will be sent an email notification about the job.

The unsuccessful return of this endpoint will be a string (starting with `ERROR:`) describing why the workflow of this endpoint did not fully complete successfully.

This `GET` will include three args, `api_key`, `obj_id` and `job_id`.

- `api_key`
   - Value is a string representing the key
- `obj_id`
   - String corresponding to the object id in mongoDB for the metadata.
- `job_id`
   - Value is a string representing the `job_id` of the failed job.

#### Example `GET` request in python
```
import requests

url = "https://ctdataservices-prod01lp.jax.org/api/archiving/retrieve_processing?api_key=KEY&obj_id=OBJ_ID&job_id=JOB_ID"

payload = {}
headers= {}

response = requests.request("GET", url, headers=headers, data=payload, verify=False)

print(response.text.encode('utf8'))
print(response.json())
```
---
### /retrieve_success
[back to top][endpoints]

This endpoint will accept a `GET` request as described below. This endpoint is used by internal components only to update the metadata with the the current status of `completed` and notify the user that their files are ready for them to access in `/fastscratch`.

The successful return will be the `job_id`. The metadata document associated with the `job_id` will be updated. The keys to update are `retrieval_status` and `when_retrieval_completed` with `"completed"` and `{timestamp}` respectively. The user will be sent an email notification about the completed job.

The unsuccessful return of this endpoint will be a string (starting with `ERROR:`) describing why the workflow of this endpoint did not fully complete successfully.

This `GET` will include three args, `api_key`, `obj_id` and `job_id`.

- `api_key`
   - Value is a string representing the key
- `obj_id`
   - String corresponding to the object id in mongoDB for the metadata.
- `job_id`
   - Value is a string representing the `job_id` of the failed job.

#### Example `GET` request in python
```
import requests

url = "https://ctdataservices-prod01lp.jax.org/api/archiving/retrieve_success?api_key=KEY&obj_id=OBJ_ID&job_id=JOB_ID"

payload = {}
headers= {}

response = requests.request("GET", url, headers=headers, data=payload, verify=False)

print(response.text.encode('utf8'))
print(response.json())
```

---
---


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

[1]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#archive
[2]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#retrieve
[3]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#get_collection
[4]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#archive_failed
[5]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#archive_processing
[6]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#archive_success
[7]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#retrieve_failed
[8]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#retrieve_processing
[9]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#retrieve_success
[frontend]: https://github.com/TheJacksonLaboratory/archive-frontend
[endpoints]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#endpoints
[metadata_link]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#metadata


<!-- SCRIPTS -->

<script>!function(t,e){"function"==typeof define&&define.amd?define([],e()):"object"==typeof module&&module.exports?module.exports=e():function n(){document&&document.body?t.zenscroll=e():setTimeout(n,9)}()}(this,function(){"use strict";var t=function(t){return t&&"getComputedStyle"in window&&"smooth"===window.getComputedStyle(t)["scroll-behavior"]};if("undefined"==typeof window||!("document"in window))return{};var e=function(e,n,o){n=n||999,o||0===o||(o=9);var i,r=function(t){i=t},u=function(){clearTimeout(i),r(0)},c=function(t){return Math.max(0,e.getTopOf(t)-o)},a=function(o,i,c){if(u(),0===i||i&&i<0||t(e.body))e.toY(o),c&&c();else{var a=e.getY(),f=Math.max(0,o)-a,s=(new Date).getTime();i=i||Math.min(Math.abs(f),n),function t(){r(setTimeout(function(){var n=Math.min(1,((new Date).getTime()-s)/i),o=Math.max(0,Math.floor(a+f*(n<.5?2*n*n:n*(4-2*n)-1)));e.toY(o),n<1&&e.getHeight()+o<e.body.scrollHeight?t():(setTimeout(u,99),c&&c())},9))}()}},f=function(t,e,n){a(c(t),e,n)},s=function(t,n,i){var r=t.getBoundingClientRect().height,u=e.getTopOf(t)+r,s=e.getHeight(),l=e.getY(),d=l+s;c(t)<l||r+o>s?f(t,n,i):u+o>d?a(u-s+o,n,i):i&&i()},l=function(t,n,o,i){a(Math.max(0,e.getTopOf(t)-e.getHeight()/2+(o||t.getBoundingClientRect().height/2)),n,i)};return{setup:function(t,e){return(0===t||t)&&(n=t),(0===e||e)&&(o=e),{defaultDuration:n,edgeOffset:o}},to:f,toY:a,intoView:s,center:l,stop:u,moving:function(){return!!i},getY:e.getY,getTopOf:e.getTopOf}},n=document.documentElement,o=function(){return window.scrollY||n.scrollTop},i=e({body:document.scrollingElement||document.body,toY:function(t){window.scrollTo(0,t)},getY:o,getHeight:function(){return window.innerHeight||n.clientHeight},getTopOf:function(t){return t.getBoundingClientRect().top+o()-n.offsetTop}});if(i.createScroller=function(t,o,i){return e({body:t,toY:function(e){t.scrollTop=e},getY:function(){return t.scrollTop},getHeight:function(){return Math.min(t.clientHeight,window.innerHeight||n.clientHeight)},getTopOf:function(t){return t.offsetTop}},o,i)},"addEventListener"in window&&!window.noZensmooth&&!t(document.body)){var r="history"in window&&"pushState"in history,u=r&&"scrollRestoration"in history;u&&(history.scrollRestoration="auto"),window.addEventListener("load",function(){u&&(setTimeout(function(){history.scrollRestoration="manual"},9),window.addEventListener("popstate",function(t){t.state&&"zenscrollY"in t.state&&i.toY(t.state.zenscrollY)},!1)),window.location.hash&&setTimeout(function(){var t=i.setup().edgeOffset;if(t){var e=document.getElementById(window.location.href.split("#")[1]);if(e){var n=Math.max(0,i.getTopOf(e)-t),o=i.getY()-n;0<=o&&o<9&&window.scrollTo(0,n)}}},9)},!1);var c=new RegExp("(^|\\s)noZensmooth(\\s|$)");window.addEventListener("click",function(t){for(var e=t.target;e&&"A"!==e.tagName;)e=e.parentNode;if(!(!e||1!==t.which||t.shiftKey||t.metaKey||t.ctrlKey||t.altKey)){if(u){var n=history.state&&"object"==typeof history.state?history.state:{};n.zenscrollY=i.getY();try{history.replaceState(n,"")}catch(t){}}var o=e.getAttribute("href")||"";if(0===o.indexOf("#")&&!c.test(e.className)){var a=0,f=document.getElementById(o.substring(1));if("#"!==o){if(!f)return;a=i.getTopOf(f)}t.preventDefault();var s=function(){window.location=o},l=i.setup().edgeOffset;l&&(a=Math.max(0,a-l),r&&(s=function(){history.pushState({},"",o)})),i.toY(a,null,s)}}},!1)}return i});</script>

</body>

</html>