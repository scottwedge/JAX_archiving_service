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
    "user_metadata": {},
    "job_id": "8638.ctarchive.jax.org",
}
'''

import config
import util

########################################################################################
## /archive_processing:

def archive_processing(args, user_dict, mongo_collection):
    '''
    Takes job_id (str);
      Returns job_id (str).

    "ready_for_pbs": false,
    "when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
    "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    +"when_archival_started": "2019-12-31 22:44:08 EDT-0400",
    "when_archival_completed": null,
    "failed_multiple": null,
    +"archival_status": "processing",
    "job_id": "8638.ctarchive.jax.org",
    '''

    job_id = args.get('job_id')
    if not job_id:
        raise Exception(util.gen_msg("No job_id passed."))

    condition = {'job_id': job_id}
    cursor = mongo_collection.find(condition, {'_id': 1})
    count = cursor.count()
    if count != 1:
        raise Exception(util.gen_msg(f"{count} records match {condition}.\n"))

    id1 = cursor[0]['_id']      ## '_id' field from 1st record (dict); type(id1): ObjectId
    result = mongo_collection.update_one(
        {'_id': id1},                                             ## match condition
        {'$set': {
             'when_archival_started': util.get_timestamp(),
             'archival_status': 'processing'}
        })
    if not result.acknowledged:
        raise Exception(util.gen_msg("MongoDB update not acknowledged."))
    
    return job_id


########################################################################################
## /archive_success:

'''
Route parameters inclde job_id (str), sourceSize (int), archivedSize (int);

    -"ready_for_pbs": false,
    *"when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
    *"when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    *"when_archival_started": "2019-12-31 22:44:08 EDT-0400",
    +"when_archival_completed": "2020-01-01 03:01:59 EDT-0400",
    -"failed_multiple": null,
    +"archival_status": "completed",
    *"job_id": "8638.ctarchive.jax.org"

then:

    "archival_status": "completed",
    "archivedSize": { "$numberInt": "396700549" },
    "dateArchived": "2020-01-01",
    "sourceSize": { "$numberInt": "797725536" },
    "submission": {
        "job_id": "8638.ctarchive.jax.org",
        "when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
        "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
        "when_archival_started": "2019-12-31 22:44:08 EDT-0400",
        "when_archival_completed": "2020-01-01 03:01:59 EDT-0400"
    }
    '''

def archive_success_proc_args(args):
    '''
    Checks for presence and correct type of arguments 'job_id, 'sourseSize', and 'archivedSize';
      Takes args (dict) with arguments from flask.request.
      Returns the tuple (job_id, sourceSize, archivedSize) after type conversions.
      Throws errors if anything missing or cannot be properly cast to right type. 
    '''

    job_id = args.get('job_id')
    if not job_id:
        raise Exception(util.gen_msg("Required parameter 'job_id' not received."))

    source_size_str = args.get('sourceSize')
    if not source_size_str:
        raise Exception(util.gen_msg(f"Required parameter 'sourceSize' not received."))

    try:
        source_size = int(source_size_str)
    except Exception as e:
        raise Exception(util.gen_msg(f"sourceSize must be an integer; got '{source_size_str}'."))

    archived_size_str = args.get('archivedSize')
    if not archived_size_str:
        raise Exception(util.gen_msg("Required parameter 'archivedSize' not received."))

    try:
        archived_size = int(archived_size_str)
    except Exception as e:
        raise Exception(util.gen_msg(f"archivedSize must be an integer; got '{archived_size_str}'."))

    return job_id, source_size, archived_size


def archive_success_make_subrecord(record):
    '''
    Makes the 'submission' subrecord.
      Takes the record.
      Returns the subrecord value (dict).
    '''

    id1 = record.get('_id')
    subrecord = {}

    for key in ['job_id', 'when_ready_for_pbs', 'when_archival_queued', 'when_archival_started']:
        if not key in record:
            raise Exception(util.gen_msg(f"Expected key '{key}' not found in record w/ id '{id1}'."))
        if not record[key]:
            raise Exception(util.gen_msg(
                f"Unexpected value '{record[key]}' for key '{key}' in record w/ id '{id1}'."))

        subrecord[key] = record[key]

    subrecord['when_archival_completed'] = util.get_timestamp()
    return subrecord


def archive_success_update_record(record, job_id, source_size, archived_size, mongo_collection):
    '''
    Does the actual mongodb update.
      Takes: 
        record, which is the pymongo version of the MongoDB record to be updated.
        job_id (str)
        source_size (int)
        archived_size (int)
      Returns _id on success; raises Exception on error.
    '''

    id1 = record.get('_id')      ## '_id' field from 1st record (dict); type(id1): ObjectId

    subrecord = archive_success_make_subrecord(record)

    result = mongo_collection.update_one(
        {'_id': id1},                                             ## match condition
        {
        '$set': {
            'archival_status': 'completed',
            'archivedSize': archived_size,
            'dateArchived': util.get_timestamp(format=config.time.get('format_day')),
            'sourceSize': source_size,
            'submission': subrecord},
        '$unset': {
            'ready_for_pbs': '',
            'failed_multiple': '',
            'when_ready_for_pbs': '',
            'when_archival_queued': '',
            'when_archival_started': '',
            'when_archival_completed': '',
            'job_id': ''}
        })

    if not result.acknowledged:
        raise Exception(util.gen_msg("MongoDB update not acknowledged."))

    return id1


def archive_success(args, user_dict, mongo_collection):
    '''
    Takes 
      args (dict) arguments from api call; includes: 
        job_id (str), sourceSize (int), archivedSize (int); 
      user_dict (dict): contains api user info; not used now;
      mongo_collection: pymongo object representing MongoDB collection;
    Returns json record (str).

    -"ready_for_pbs": false,
    *"when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
    *"when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    *"when_archival_started": "2019-12-31 22:44:08 EDT-0400",
    +"when_archival_completed": "2020-01-01 03:01:59 EDT-0400",
    -"failed_multiple": null,
    +"archival_status": "completed",
    *"job_id": "8638.ctarchive.jax.org"

    then:

    "archival_status": "completed",
    "archivedSize": { "$numberInt": "396700549" },
    "dateArchived": "2020-01-01",
    "sourceSize": { "$numberInt": "797725536" },
    "submission": {
        "job_id": "8638.ctarchive.jax.org",
        "when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
        "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
        "when_archival_started": "2019-12-31 22:44:08 EDT-0400",
        "when_archival_completed": "2020-01-01 03:01:59 EDT-0400"
    }
    '''

    job_id, source_size, archived_size = archive_success_proc_args(args)

    condition = {'job_id': job_id}
    cursor = mongo_collection.find(condition)
    count = cursor.count()
    if count != 1:
        raise Exception(util.gen_msg(f"{count} records match {condition}."))

    id1 = archive_success_update_record(cursor[0], job_id, source_size, archived_size, mongo_collection)

    cursor = mongo_collection.find({'_id': id1})
    count = cursor.count()
    if count != 1:
        raise Exception(util.gen_msg(f"{count} records match _id '{id1}'."))
    
    return str(cursor[0])


########################################################################################
## /archive_failed:

## takes job_id; returns error msg from pbs;
##   archival_status -> failed; 
##   when_archival_failed -> e.g. ??????:

def archive_failed(args, user_dict, mongo_collection):
    '''
    "ready_for_pbs": false,
    "when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
    "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    "when_archival_started": "2019-12-31 22:41:02 EDT-0400",
    "when_archival_failed": "2019-12-31 22:46:08 EDT-0400",
    "when_archival_completed": null,
    "failed_multiple": null,
    "archival_status": "failed"
    '''
    return user_dict


########################################################################################
## /retrieve_processing:

## takes obj_id, job_id; returns job_id;
##   retrieval_status -> processing; 
##   when_retrieval_started -> e.g. ??????:

def retrieve_processing(args, user_dict, mongo_collection):
    return user_dict


########################################################################################
## /retrieve_success:

## takes obj_id, job_id; returns job_id;
##   retrieval_status -> completed; 
##   when_retrieval_completed -> e.g. ??????;

def retrieve_success(args, user_dict, mongo_collection):
    return user_dict


########################################################################################
## /retrieve_failed:

## takes obj_id, job_id; returns error msg from pbs along with job_id;
##   retrieval_status -> failed; 
##   when_retrieval_completed -> None 

def retrieve_failed(args, user_dict, mongo_collection):
    return user_dict


