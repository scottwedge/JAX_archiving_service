# JAX Archiving Service
### Tier 3 archiving microservice

[![N|Solid](https://clic-ctsa.org/sites/default/files/styles/large/public/2019-10/jacksonLabLogo.png)](https://jacksonlaboratory.sharepoint.com/sites/ResearchIT)

# API Documentation

## Endpoints

- [`/archive`][1]
   - [metadata][metadata_link]
- [`/retrieve`][2]
- [collection-endpoints][3]
   - [`/get_documents`][10]
   - [`/get_document_by_id`][11]
   - [`/get_last_document`][12]
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
-   `user_metadata` This key is required, however, the value (if any) is specified by the user.

---
#### Example Metadata Queued
Example of [metadata][metadata_queued] when initially inserted into mongoDB
```
{
    "managerUserId": "pi",
    "userId": "postdoc",
    "projectName": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "group": "science-lab",
        "email": "post.doc@jax.org"
    },
    "archivedPath": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "sourceFolderPath": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "ready_for_submit": false,
    "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    "when_archival_started": null,
    "when_archival_completed": null,
    "failed_multiple": null,
    "archival_status": "queued",
    "user_metadata":{}
}
```
---
Example of metadata when archiving is completed
```
{
    "managerUserId": "pi",
    "userId": "postdoc",
    "projectName": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archivedPath": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "sourceFolderPath": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "archival_status": "completed",
    "archivedSize": {
        "$numberInt": "396700549"
    },
    "dateArchived": "2020-01-01",
    "sourceSize": {
        "$numberInt": "797725536"
    },
    "user_metadata":{},
    "submission": {
        "job_id": "8638.ctarchive.jax.org",
        "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
        "when_archival_started": "2019-12-31 22:41:02 EDT-0400",
        "when_archival_completed": "2020-01-01 03:01:59 EDT-0400"
    }
}
```

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
        "request_type": "singlecell",
        "user_metadata":{}
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
---
#### Retrieval Current User
To keep track of the user, the user info for the `api_key` holder will be temporarily entered into the metadata so that the email associated with an `api_key` will receive the email notifications. The key with this current user is `current_user`.

Example of metadata while retrieve processing
```
{
	"current_user": {
    "fname": "Research",
    "lname": "IT",
    "username": "rit",
    "email": "rit@jax.org"
	},
    "managerUserId": "pi",
    "userId": "postdoc",
    "projectName": "Nobel Prize Project (NPP)",
    "classification": "topSecret",
    "grant_id": "NA",
    "notes": "Who needs notes?",
    "request_type": "faculty",
    "system_groups": ["jaxuser"],
    "submitter": {
        "fname": "post",
        "lname": "doc",
        "username": "pdoc",
        "email": "post.doc@jax.org"
    },
    "archivedPath": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP",
    "sourceFolderPath": "/tier2/pi-lab/postdoc/postdoc_NPP",
    "archival_status": "completed",
    "submit_progress": [],
    "archivedSize": {
        "$numberInt": "396700549"
    },
    "dateArchived": "2020-05-19",
    "sourceSize": {
        "$numberInt": "797725536"
    },
    "user_metadata":{},
    "submission": {
        "job_id": "8638.ctarchive.jax.org",
        "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
        "when_archival_started": "2019-12-31 22:41:02 EDT-0400",
        "when_archival_completed": "2020-01-01 03:01:59 EDT-0400"
    },
    "retrievals": [{
    "job_id": "6404.ctarchive.jax.org",
    "retrieval_status": "failed",
    "when_retrieval_queued": "2020-03-30 12:32:14 EDT-0400",
    "when_retrieval_started": "2020-03-30 12:32:15 EDT-0400",
    "when_retrieval_completed": null
}, {
    "job_id": "6406.ctarchive.jax.org",
    "retrieval_status": "completed",
    "when_retrieval_queued": "2020-03-30 13:48:41 EDT-0400",
    "when_retrieval_started": "2020-03-30 13:48:43 EDT-0400",
    "when_retrieval_completed": "2020-03-30 14:12:21 EDT-0400"
}, {
    "job_id": "6628.ctarchive.jax.org",
    "retrieval_status": "completed",
    "when_retrieval_queued": "2020-05-12 16:25:31 EDT-0400",
    "when_retrieval_started": "2020-05-12 16:25:32 EDT-0400",
    "when_retrieval_completed": "2020-05-12 17:54:42 EDT-0400"
    }]
}
```


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
## collection endpoints
[back to top][endpoints]

These endpoints will accept a `GET` request as described below. These endpoints will primarily be used by the [archive frontend][frontend].

### /get_documents

The return value is a list of documents specified by the args. This `GET` will include four args `api_key`, `find`, `limit` and `last`.
- `api_key`
   - Value is the string representing the key
- `find`
   - dict with key,value pair used to filter results in collection. In most cases the value of this dict will be `{"archival_status": "completed"}`
- `limit`
  - integer corresponding to the number of documents to limit the return to. In most cases this will be `100`.
- `last`
  - the `object id` of the last `limit` number documents after sorting.


### /get_document_by_objectid

The return value is the document corresponding to the specified `object_id`. This `GET` will include two args `api_key` and `object_id`.
- `api_key`
   - Value is the string representing the key
- `object_id`
   - string value of the object id you want to query


### /get_last_document

The return value is the last document in the mongoDB collection. This `GET` will include one arg `api_key`.
- `api_key`
   - Value is the string representing the key


#### example of `GET` request in python
```
import requests

# get_documents
url = "https://ctdataservices-prod01lp.jax.org/api/archiving/get_documents?api_key=KEY&find={\"archival_status\":\"completed\"}&limit=null&last=null"

# get_document_by_objectid
url = "https://ctdataservices-prod01lp.jax.org/api/archiving/get_document_by_objectid?api_key=KEY&_id=5ac0cafa824137ec055665b9"

# get_last_document
url = "https://ctdataservices-prod01lp.jax.org/api/archiving/get_last_document?api_key=KEY"

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

---
Example of [metadata][metadata_archive_processing] state after this endpoint updates the metadata


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

The successful return will be the `gold_document` (a python dictionary) containing the metadata. The metadata document associated with the `job_id` will be updated. The keys to update are `archival_status`, `when_archival_completed`, `sourceSize`, `archivewdSize` and `dateArchived` with `"success"` and `{timestamp}` respectively. The user will be sent an email notification about the successfully completed job.

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

 ---
 Example of [metadata][metadata_archive_completed] state after this endpoint updates the metadata

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

## Archiving General Overall Diagram

![archiving diagram](https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/Archiving_Diagram_JAS.png "Archiving Diagram")


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

[1]: #archive
[2]: #retrieve
[3]: #collection-endpoints
[4]: #archive_failed
[5]: #archive_processing
[6]: #archive_success
[7]: #retrieve_failed
[8]: #retrieve_processing
[9]: #retrieve_success
[10]: #get_documents
[11]: #get_document_by_objectid
[12]: #get_last_document
[frontend]: https://github.com/TheJacksonLaboratory/archive-frontend
[endpoints]: #endpoints
[metadata_link]: #metadata
<!-- [example_metadata_queued]: #example-metadata-queued -->
[metadata_archive_queued]: metadata.md#metadata-archive-queued
[metadata_archive_processing]: metadata.md#metadata-archive-processing
[metadata_archive_completed]: metadata.md#metadata-archive-completed
