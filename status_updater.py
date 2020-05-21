'''
Before archive_processing() is called, record looks like:
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
'''

## takes job_id; returns job_id;
##   archival_status -> processing; 
##   when_archival_started -> e.g. "2020-01-28 15:46:36 EST-0500":

def archive_processing(args, user_dict, mongo_collection):
    '''
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
    "when_archival_started": "2019-12-31 22:41:02 EDT-0400",
    "when_archival_completed": null,
    "failed_multiple": null,
    "archival_status": "processing",
    "user_metadata":{}
    }
    '''
    return user_dict


## takes job_id, sourceSize, archivedSize; ???returns json string record;???
##   archival_status -> ???processing???; 
##   when_archival_completed -> e.g. "2020-03-04 15:13:42 EST-0500";
##   sourceSize -> sourceSize; 
##   archivedSize -> archivedSize, 
##   dateArchived -> e.g. "2020-03-04":

def archive_success(args, user_dict, mongo_collection):
    '''
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
    '''
    return user_dict


## takes job_id; returns error msg from pbs;
##   archival_status -> failed; 
##   when_archival_failed -> e.g. ??????:

def archive_failed(args, user_dict, mongo_collection):
    return user_dict


## takes obj_id, job_id; returns job_id;
##   retrieval_status -> processing; 
##   when_retrieval_started -> e.g. ??????:

def retrieve_processing(args, user_dict, mongo_collection):
    return user_dict


## takes obj_id, job_id; returns job_id;
##   retrieval_status -> completed; 
##   when_retrieval_completed -> e.g. ??????;

def retrieve_success(args, user_dict, mongo_collection):
    return user_dict


## takes obj_id, job_id; returns error msg from pbs along with job_id;
##   retrieval_status -> failed; 
##   when_retrieval_completed -> None 

def retrieve_failed(args, user_dict, mongo_collection):
    return user_dict


