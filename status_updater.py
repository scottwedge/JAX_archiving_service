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
    "when_archival_queued": null,
    "when_archival_started": null,
    "when_archival_completed": null,
    "failed_multiple": null,
    "archival_status": "ready_to_submit",
    "user_metadata": {},
}
'''

## global imports:

import bson.objectid

## local imports:

import config
import util

########################################################################################
## argument handling:

def get_args_objid_jobid(args):
    '''
    Takes args (dict) with str values for keys 'obj_id' and 'job_id';
    Returns values for 'obj_id' (bson.objectid.ObjectId) and 'job_id' (str);
    '''

    obj_id = args.get('obj_id')
    if not obj_id:
        raise Exception(util.gen_msg("No obj_id passed."))

    try:
        id1 = bson.objectid.ObjectId(obj_id)
    except Exception as e:
        raise Exception(util.gen_msg("obj_id '{obj_id}' not valid: {e}"))

    job_id = args.get('job_id')
    if not job_id:
        raise Exception(util.gen_msg("No job_id passed."))

    return id1, job_id


########################################################################################
## /archive_queued:

def archive_queued(args, user_dict, mongo_collection):
    '''
    Takes obj_id, job_id (str)
      Returns job_id

    "ready_for_pbs": false,
    "when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
    "+when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    "when_archival_started": null,
    "when_archival_completed": null,
    "failed_multiple": null,
    "*archival_status": "queued",
    "+job_id": "8638.ctarchive.jax.org",
    '''

    obj_id, job_id = get_args_objid_jobid(args)

    condition = {'_id': obj_id}
    cursor = mongo_collection.find(condition, {'_id': 1})
    count = cursor.count()
    if count != 1:
        raise Exception(util.gen_msg(f"{count} records match {condition}.\n"))

    result = mongo_collection.update_one(
        {'_id': obj_id},                                             ## match condition
        {'$set': {
             'when_archival_queued': util.get_timestamp(),
             'archival_status': 'queued',
             'job_id': job_id}
        })

    if not result.acknowledged:
        raise Exception(util.gen_msg(f"MongoDB update on _id '{obj_id}' not acknowledged."))

    return job_id


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
        raise Exception(util.gen_msg(f"MongoDB update on _id '{id1}' not acknowledged."))
    
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
        raise Exception(util.gen_msg("MongoDB update on _id '{id1}' not acknowledged."))

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

def archive_failed(args, user_dict, mongo_collection):
    '''
    Marks archive record as having failed. 
      Takes job_id;
      Returns ???'error msg from pbs'???
    from:
    "ready_for_pbs": false,
    "when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
    "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    "when_archival_started": "2019-12-31 22:44:08 EDT-0400",
    "when_archival_completed": null,
    "failed_multiple": null,
    "archival_status": "processing",
    "job_id": "8638.ctarchive.jax.org",

    to:
    "ready_for_pbs": false,
    "when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
    "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
    "when_archival_started": "2019-12-31 22:41:02 EDT-0400",
    +"when_archival_failed": "2019-12-31 22:46:08 EDT-0400",
    "when_archival_completed": null,
    "failed_multiple": null,
    *"archival_status": "failed",
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
             'when_archival_failed': util.get_timestamp(),
             'archival_status': 'failed'}
        })

    if not result.acknowledged:
        raise Exception(util.gen_msg("MongoDB update on _id '{id1}' not acknowledged."))

    return job_id

########################################################################################
## find matching retrievals records:

def get_retrievals_list(mongo_record):

    if not isinstance(mongo_record, dict):
        raise Exception(util.gen_msg(
            f"expected mongo_record to be dict; got: '{type(mongo_record)}'; record: {mongo_record}"
        ))

    retrievals = mongo_record.get('retrievals')
    if not retrievals:
        raise Exception(util.gen_msg(
            f"unexpectedly mongo_record does not have 'retrievals' key; record: {mongo_record}"
        ))
    if not isinstance(retrievals, list):
        raise Exception(util.gen_msg(
            f"expected 'retrievals' to be list; got: '{type(retrievals)}'; record: {mongo_record}"
        ))

    return retrievals


def get_retrievals_indices(job_id, status, mongo_record):

    only_one_allowed = ['ready_for_pbs', 'queued']
    pre_jobid_status = 'ready_for_pbs'

    retrievals = get_retrievals_list(mongo_record)

    idx_list = []
    for idx in range(len(retrievals)):
        if not isinstance(retrievals[idx], dict):
            continue
        status_idx = retrievals[idx].get('retrieval_status')

        if status == pre_jobid_status:
            if status_idx == status:
                idx_list.append(idx)
        elif job_id == retrievals[idx].get('job_id'):
            if status_idx != status:
                raise Exception(util.gen_msg(
                    f"Found job_id '{job_id}', but retrieval status '{status_idx}', "
                    + f"expected '{status}'; record: {mongo_record}"
                ))
            idx_list.append(idx)

    return idx_list


def get_retrievals_idx(job_id, status, mongo_record):
    '''
    Searches mongo_record.retrievals (list of dicts) for subrecord (dict) with 
      matching job_id and retrieval_status; if no matching job_id, but finds
      subrecord with same status and no job_id set, returns the index of the 
      first such subrecord.
    Takes: 
      job_id for retrieval
      status: expected retrieval_status for the matching retrieval
      mongo_record: mongodb record (dict) to be searched.
    Returns:
      index (int >= 0) of best matching subrecord in mongo_record.retrievals list.
    '''

    only_one_allowed = ['ready_for_pbs', 'queued']
    pre_jobid_status = 'ready_for_pbs'

    idx_list = get_retrievals_indices(job_id, status, mongo_record)

    if len(idx_list) == 1:
        return idx_list[0]
    elif len(idx_list) == 0:
        if status == pre_jobid_status:
            raise Exception(util.gen_msg(
                f"Could not find status '{status}' in record: {mongo_record}"
            ))
        else: 
            raise Exception(util.gen_msg(
                f"Could not find retrieval job_id '{job_id}' w/ status '{status}' "
                + f"in record: {mongo_record}"
            ))
    elif status == pre_job_id_status:
        raise Exception(util.gen_msg(
            f"{len(idx_list)} matches {idx_list} found w/ status '{status}' "
            + f"in record: {mongo_record}"
        )) 
    else:
        raise Exception(util.gen_msg(
            f"{len(idx_list)} matches {idx_list} found w/ status '{status}' "
            + f"in record: {mongo_record}"
        ))


########################################################################################
## /retrieve_queued:

def retrieve_queued(args, user_dict, mongo_collection):
    '''
    Takes: 
      args (dict) with obj_id (str), job_id (str);
      user_dict (dict) not used;
      mongo_collection: MongoDB database.collection
    Returns:
      job_id (str)

    from:
    "retrievals": [{
      "retrieval_status": "ready_for_pbs",
      "when_ready_for_pbs": "2020-01-02 07:34:38 EDT-0400",
      "when_retrieval_queued": null,
      "when_retrieval_started": null,
      "when_retrieval_completed": null}]

    to:
    "retrievals": [{
      +"job_id": "8649.ctarchive.jax.org",
      *"retrieval_status": "queued",
      "when_ready_for_pbs": "2020-01-02 07:34:38 EDT-0400",
      *"when_retrieval_queued": "2020-01-02 07:34:39 EDT-0400",
      "when_retrieval_started": null,
      "when_retrieval_completed": null}]
    '''

    expected_status = 'ready_for_pbs'

    obj_id, job_id = get_args_objid_jobid(args)

    condition = {'_id': obj_id}
    cursor = mongo_collection.find(condition)
    if cursor.count() != 1:
        raise Exception(util.gen_msg(f"{count} records match {condition}.\n"))

    idx = get_retrievals_idx(job_id, expected_status, cursor[0])
    prefix = 'retrievals.' + str(idx)

    result = mongo_collection.update_one(
        {'_id': obj_id},
        {'$set': {
            f'{prefix}.job_id': job_id,
            f'{prefix}.retrieval_status': 'queued',
            f'{prefix}.when_retrieval_queued': util.get_timestamp()}
        })

    if not result.acknowledged:
        raise Exception(util.gen_msg(f"MongoDB update on _id '{obj_id}' not acknowledged."))

    return job_id


########################################################################################
## /retrieve_processing:

def retrieve_processing(args, user_dict, mongo_collection):
    '''
    Changes status of retrieval job matching args['obj_id'] and args['job_id'] 
      from 'queued' to 'processing'.
    Takes:
      args (dict) with obj_id (str), job_id (str);
      user_dict (dict) not used;
      mongo_collection: MongoDB database.collection
    Returns:
      job_id (str)
 
    MongoDB record changed from:
    "retrievals": [{
      "job_id": "8649.ctarchive.jax.org",
      "retrieval_status": "queued",
      "when_ready_for_pbs": "2020-01-02 07:34:38 EDT-0400",
      "when_retrieval_queued": "2020-01-02 07:34:39 EDT-0400",
      "when_retrieval_started": null,
      "when_retrieval_completed": null
    }]

    to:
    "retrievals": [{
      "job_id": "8649.ctarchive.jax.org",
      *"retrieval_status": "processing",
      "when_ready_for_pbs": "2020-01-02 07:34:38 EDT-0400",
      "when_retrieval_queued": "2020-01-02 07:34:39 EDT-0400",
      *"when_retrieval_started": "2020-01-02 07:36:25 EDT-0400",
      "when_retrieval_completed": null
    }]
    '''

    expected_status = 'queued'

    obj_id, job_id = get_args_objid_jobid(args)

    condition = {'_id': obj_id}
    cursor = mongo_collection.find(condition)
    if cursor.count() != 1:
        raise Exception(util.gen_msg(f"{count} records match {condition}.\n"))

    idx = get_retrievals_idx(job_id, expected_status, cursor[0])
    prefix = 'retrievals.' + str(idx)

    result = mongo_collection.update_one(
        {'_id': obj_id},
        {'$set': {
            f'{prefix}.retrieval_status': 'processing',
            f'{prefix}.when_retrieval_started': util.get_timestamp()}
        })

    if not result.acknowledged:
        raise Exception(util.gen_msg(f"MongoDB update on _id '{obj_id}' not acknowledged."))

    return job_id


########################################################################################
## /retrieve_success:

def get_current_username(mongo_record):

    if not isinstance(mongo_record, dict):
        raise Exception(util.gen_msg(
            f"expected mongo_record to be dict; got: '{type(mongo_record)}'; record: {mongo_record}"
        ))

    if 'current_user' not in mongo_record:
        raise Exception(util.gen_msg(
            f"key 'current_user' not found in record: {mongo_record}"
        ))

    user_obj = mongo_record.get('current_user')

    if not isinstance(user_obj, dict):
        raise Exception(util.gen_msg(
            f"current_user expected to be dict, got '{type(user_obj)}'."
        ))

    if 'username' not in user_obj:
        raise Exception(util.gen_msg(
            f"key 'username' not found in current_user in record: {mongo_record}"
        ))

    username = user_obj.get('username')
    if not (username and isinstance(username, str)):
        raise Exception(util.gen_msg(
            f"username not specified or not str in current_user in record: {mongo_record}"
        ))

    return username
 

## takes obj_id, job_id; returns job_id;

def retrieve_success(args, user_dict, mongo_collection):
    '''
    Changes status of retrieval job matching args['obj_id'] and args['job_id']
      from 'processing' to 'completed'.
    Takes:
      args (dict) with obj_id (str), job_id (str);
      user_dict (dict) not used;
      mongo_collection: MongoDB database.collection
    Returns:
      job_id (str)

    Meta-data updated from:
    "current_user": {
      "fname": "Research",
      "lname": "IT",
      "username": "rit",
      "email": "rit@jax.org"
    },
    "retrievals": [{
      "job_id": "8649.ctarchive.jax.org",
      "retrieval_status": "processing",
      "when_ready_for_pbs": "2020-01-02 07:34:38 EDT-0400",
      "when_retrieval_queued": "2020-01-02 07:34:39 EDT-0400",
      "when_retrieval_started": "2020-01-02 07:36:25 EDT-0400",
      "when_retrieval_completed": null
    }]

    to:
    -"current_user": ...,
    "retrievals": [{
      +"username": "rit",
      "job_id": "8649.ctarchive.jax.org",
      *"retrieval_status": "completed",
      "when_ready_for_pbs": "2020-01-02 07:34:38 EDT-0400",
      "when_retrieval_queued": "2020-01-02 07:34:39 EDT-0400",
      "when_retrieval_started": "2020-01-02 07:36:25 EDT-0400",
      *"when_retrieval_completed": "2020-01-02 13:42:53 EDT-0400",
    }]
    '''

    expected_status = 'processing'

    obj_id, job_id = get_args_objid_jobid(args)

    condition = {'_id': obj_id}
    cursor = mongo_collection.find(condition)
    if cursor.count() != 1:
        raise Exception(util.gen_msg(f"{count} records match {condition}.\n"))

    idx = get_retrievals_idx(job_id, expected_status, cursor[0])
    prefix = 'retrievals.' + str(idx)

    username = get_current_username(cursor[0])

    result = mongo_collection.update_one(
        {'_id': obj_id},
        {'$set': {
            f'{prefix}.username': username,
            f'{prefix}.retrieval_status': 'completed',
            f'{prefix}.when_retrieval_completed': util.get_timestamp()},
         '$unset': { 'current_user': '' }})

    if not result.acknowledged:
        raise Exception(util.gen_msg(f"MongoDB update on _id '{obj_id}' not acknowledged."))

    return job_id


########################################################################################
## /retrieve_failed:

## takes obj_id, job_id; returns error msg from pbs along with job_id;
##   retrieval_status -> failed; 
##   when_retrieval_completed -> None 

def retrieve_failed(args, user_dict, mongo_collection):
    '''
    Takes:
      obj_id:
      job_id:
    Returns: 
      error_msg from pbs
      job_id

    Meta-data changed from:
    -"current_user": {
        "fname": "Research",
        "lname": "IT",
        "username": "rit",
        "email": "rit@jax.org",
    },
    ...
    "retrievals": [{
        "job_id": "8649.ctarchive.jax.org",
        *"retrieval_status": "processing",
        "when_ready_for_pbs": "2020-01-02 07:34:38 EDT-0400",
        "when_retrieval_queued": "2020-01-02 07:34:39 EDT-0400",
        "when_retrieval_started": "2020-01-02 07:36:25 EDT-0400",
        "when_retrieval_completed": null,
    }]

    to:
    "retrievals": [{
        "job_id": "8649.ctarchive.jax.org",
        *"retrieval_status": "failed",
        "when_ready_for_pbs": "2020-01-02 07:34:38 EDT-0400",
        "when_retrieval_queued": "2020-03-30 12:32:14 EDT-0400",
        "when_retrieval_started": "2020-03-30 12:32:15 EDT-0400",
        "when_retrieval_completed": null,
        +"when_retrieveal_failed": "2020-03-30 14:46:58 EDT-0400",
        +"username": "rit",
    }]
    '''

    expected_status = 'processing'

    obj_id, job_id = get_args_objid_jobid(args)

    condition = {'_id': obj_id}
    cursor = mongo_collection.find(condition)
    if cursor.count() != 1:
        raise Exception(util.gen_msg(f"{count} records match {condition}.\n"))

    idx = get_retrievals_idx(job_id, expected_status, cursor[0])
    prefix = 'retrievals.' + str(idx)

    username = get_current_username(cursor[0])

    result = mongo_collection.update_one(
        {'_id': obj_id},
        {'$set': {
            f'{prefix}.username': username,
            f'{prefix}.retrieval_status': 'failed',
            f'{prefix}.when_retrieval_failed': util.get_timestamp()},
         '$unset': { 'current_user': '' }})

    if not result.acknowledged:
        raise Exception(util.gen_msg(f"MongoDB update on _id '{obj_id}' not acknowledged."))

    return f"{job_id}: need to update code to retrieve PBS error message here."

