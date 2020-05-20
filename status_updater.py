## takes job_id; returns job_id;
##   archival_status -> processing; 
##   when_archival_started -> e.g. "2020-01-28 15:46:36 EST-0500":

def archive_processing(args, user_dict, mongo_collection):
    return user_dict


## takes job_id, sourceSize, archivedSize; ???returns json string record;???
##   archival_status -> ???processing???; 
##   when_archival_completed -> e.g. "2020-03-04 15:13:42 EST-0500";
##   sourceSize -> sourceSize; 
##   archivedSize -> archivedSize, 
##   dateArchived -> e.g. "2020-03-04":

def archive_success(args, user_dict, mongo_collection):
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


