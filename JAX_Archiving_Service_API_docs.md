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

This endpoint will accept a valid `POST` archiving request as described below. The successful return for this endpoint is the object id of the metadata in mongoDB. A successful return means your request was successfully submitted to pbs and further updates on the status of the archiving event will be directed by pbs via this archiving microservice.

An unsuccessful return value will be a string (starting with `ERROR:`) describing why the request was not submitted to pbs.

The body of the `POST` request must contain the following keys [`api_key`, `metadata`, `source_folder`, `service_path`]
- `api_key`
   - Value is the string representing the key
- `metadata`
   - Value is a dictionary containing some required keys. Described in more detail below [click here][metadata_link].
- `source_folder`
   - String representing the absolute path to the directory requested to be archived
- `service_path`
   - Not applicable for requests to archive `faculty` data
   - Applicable for any of the services. Presently there are only two services archiving data (single cell & microscopy)
   - The user specified path in the archive after `/archive/services/<singlecell or microscopy>/`
   - The service will generate the correct prefix with the appropriate service name `singlecell` or `microscopy`

##### `metadata`
[back to /archive][1]

A dictionary with the following required keys [`manager_user_id`, `user_id`, `project_name`, `grant_id`, `notes`, `system_groups`, `request_type`]
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
3. When pbs starts to process the job it will use the `archive_processing` endpoint with the `job_id`. 
   - This will notify user and update metadata.
4. When the job is completed, pbs will use the `archive_success` endpoint with `job_id`, `sourceSize` and `archivedSize`
   - This will notify user and update metadata.

#### Example `archive` request
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

This endpoint will accept a valid `POST` retrieve request as described below. The successful return will be an integer corresponding to the number of directories submitted for retrieval.

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

#### Example `retrieve` request
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
headers = {
		'Content-Type': 'application/json',
		'Content-Type': 'text/plain'
}

response = requests.request("POST", url, headers=headers, data=payload, verify=False)

print(response.text.encode('utf8'))
print(response.json())
```
---
### /get_collection
[back to top][endpoints]

This endpoint will accept a `GET` request as described below. The successful return will be a mongoDB collection of documents. This endpoint is primarily to be used by the [archive frontend][frontend].

This `GET` will include two args `api_key` and `gold`
- `api_key`
   - Value is the string representing the key
- `gold`
   - boolean, `true` for permanently archived metadata, `false` for operational metadata

#### example of `GET` request
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

This endpoint will accept a `GET` request as described below. The successful return will be a string stating that the metadata was successfully updated along with the `job_id`. The metadata document associated with the `job_id` will be updated. The keys to update are `archival_status` and `when_archival_failed` with `"failed"` and `{timestamp}` respectively. The data services team will be sent an email notification about the failed job.

This `GET` will include two args, `api_key` and `job_id`.

- `api_key`
   - Value is a string representing the key
- `job_id`
   - Value is a string representing the `job_id` of the failed job.

#### Example of `GET` request
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

This endpoint will accept a `GET` request as described below. The successful return will be a string stating that the metadata was successfully updated along with the `job_id`. The metadata document associated with the `job_id` will be updated. The keys to update are `archival_status` and `when_archival_started` with `"processing"` and `{timestamp}` respectively. The data services team will be sent an email notification about the failed job.

This `GET` will include two args, `api_key` and `job_id`.

- `api_key`
   - Value is a string representing the key
- `job_id`
   - Value is a string representing the `job_id` of the failed job.

#### Example of `GET` request
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

This endpoint will accept a `GET` request as described below. The successful return will be the `gold_document` (a python dictionary) containning the metadata. The metadata document associated with the `job_id` will be updated. The keys to update are `archival_status`, `when_archival_completed`, `sourceSize`, `archivewdSize` and `dateArchived` with `"processing"` and `{timestamp}` respectively. The user will be sent an email notification about the successfully completed job.

This `GET` will include two args, `api_key` and `job_id`.

- `api_key`
   - Value is a string representing the key
- `job_id`
   - Value is a string representing the `job_id` of the failed job.

#### Example of `GET` request
```
import requests

url = "https://ctdataservices-prod01lp.jax.org/api/archiving/archive_success?api_key=KEY&job_id=archive.1&sourceSize=INTEGER&archivedSize=INTEGER"

payload = {}
headers= {}

response = requests.request("GET", url, headers=headers, data = payload)

print(response.text.encode('utf8'))
print(response.json())
```

---
---
---

#### Example article excerpt

> Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.


| Example | Table |
| ------ | ------ |
| Dropbox | [plugins/dropbox/README.md][PlDb] |
| GitHub | [plugins/github/README.md][PlGh] |
| Google Drive | [plugins/googledrive/README.md][PlGd] |
| OneDrive | [plugins/onedrive/README.md][PlOd] |
| Medium | [plugins/medium/README.md][PlMe] |
| Google Analytics | [plugins/googleanalytics/README.md][PlGa] |



[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)


   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>
   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>

[1]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#archive
[2]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#retrieve
[3]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#get_collection
[4]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#archive_failed
[5]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#archive_processing
[6]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#archive_success
[7]: https://www.google.com
[8]: https://www.google.com
[9]: https://www.google.com
[frontend]: https://github.com/TheJacksonLaboratory/archive-frontend
[endpoints]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#endpoints
[metadata_link]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#metadata