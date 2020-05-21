### Examples of metadata state at various stages of archiving and retrieving

---
#### Metadata when ready for mongoDB
Example of metadata when initially inserted into mongoDB
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
    "ready_for_pbs": true,
    "when_ready_for_pbs": null,
    "when_archival_queued": null,
    "when_archival_started": null,
    "when_archival_completed": null,
    "failed_multiple": null,
    "archival_status": "ready_for_mongo",
    "user_metadata":{},
}
```

Back to [archive][metadata_link]

---
#### Metadata after initially inserted
Example of metadata when initially inserted into mongoDB
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
    "ready_for_pbs": false,
    "when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
    "when_archival_queued": null,
    "when_archival_started": null,
    "when_archival_completed": null,
    "failed_multiple": null,
    "archival_status": "ready_to_submit",
    "user_metadata":{},
}
```

Back to [archive][metadata_link]

---
#### Metadata archive queued
Example of metadata when initially inserted into mongoDB
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
    "ready_for_pbs": false,
    "when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
    "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    "when_archival_started": null,
    "when_archival_completed": null,
    "failed_multiple": null,
    "archival_status": "queued",
    "user_metadata":{},
    "job_id": "8638.ctarchive.jax.org",
}
```

Back to [archive][metadata_link]

---
#### Metadata archive processing
Example of metadata state when `/archive_processing` updates metadata
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
    "ready_for_pbs": false,
    "when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
    "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    "when_archival_started": "2019-12-31 22:41:02 EDT-0400",
    "when_archival_completed": null,
    "failed_multiple": null,
    "archival_status": "processing",
    "user_metadata":{},
    "job_id": "8638.ctarchive.jax.org",
}
```

Back to [`/archive_processing`][5]

---

#### Metadata archive completed
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
        "when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
        "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
        "when_archival_started": "2019-12-31 22:41:02 EDT-0400",
        "when_archival_completed": "2020-01-01 03:01:59 EDT-0400"
    }
}
```

Back to [`/archive_success`][6]

---

#### Metadata archive failed
Example of metadata state when `/archive_failed` updates metadata. Note that metadata state can look different from example below depending on what stage of archiving process the failure happens.
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
    "ready_for_pbs": false,
    "when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
    "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    "when_archival_started": "2019-12-31 22:41:02 EDT-0400",
    "when_archival_failed": "2019-12-31 22:46:08 EDT-0400",
    "when_archival_completed": null,
    "failed_multiple": null,
    "archival_status": "failed",
    "user_metadata":{}
}
```

Back to [`/archive_failed`][4]



[1]: README.md#archive
[2]: README.md#retrieve
[3]: README.md#collection-endpoints
[4]: README.md#archive_failed
[5]: README.md#archive_processing
[6]: README.md#archive_success
[7]: README.md#retrieve_failed
[8]: README.md#retrieve_processing
[9]: README.md#retrieve_success
[10]: README.md#get_documents
[11]: README.md#get_document_by_objectid
[12]: README.md#get_last_document
[frontend]: https://github.com/TheJacksonLaboratory/archive-frontend
[endpoints]: README.md#endpoints
[metadata_link]: README.md#metadata
[example_metadata]: README.md#example-metadata
