## global imports:

import pymongo
import bson.objectid
import json

## local imports:

import config
import util


def record_permitted(record, user_dict):
    '''
    Returns True if user has permissions on record; else False
    '''

    if user_dict.get('admin'):
        return True

    user_groups_list = user_dict.get('groups_list')

    if not isinstance(user_groups_list, list):
        raise Exception(util.gen_msg(
            f"user_dict['groups_list'] '{user_groups_list}' is not a list; user_dict: '{user_dict}'"
        ))

    if 'system_groups' not in record:
        util.log_email(util.gen_msg(
            f"record has no system_groups key; record: '{record}'"
        ))
        return False

    allowed_groups_list = record.get('system_groups')

    if not isinstance(allowed_groups_list, list):
        util.log_email(util.gen_msg(
            f"record['groups_list'] '{allowed_groups_list}' is not a list; record: '{record}'"
        ))

    for group in allowed_groups_list:
        if group in user_groups_list:
            return True

    return False


def get_permitted_records_list(user_dict, cursor, start_after_id=None, limit=float("inf")):

    records = []

    if start_after_id: 
        found_start = False
    else: 
        found_start = True

    for record in cursor:

        if found_start:
            if record_permitted(record, user_dict):
                records.append(record)
            if len(records) >= limit:
                return records
        else:   
            if '_id' not in record:
                raise Exception("_id field not returned by query filter.")

            id1 = str(record.get("_id"))
            if id1 == start_after_id:
                found_start = True

    return records


def get_documents(args, user_dict, mongo_collection):

    condition = args.get('find')
    limit = args.get('limit')
    last = args.get('last')

    try:
        condition = json.loads(condition)
    except Exception as e:
        raise Exception(util.gen_msg(f"Could not parse dict from '{condition}'."))

    cursor = mongo_collection.find(condition)

    records = get_permitted_records_list(user_dict, cursor, start_after_id=last, limit=limit)
    records = json.dumps(records)

    return f"type(records): '{type(records)}'; condition: '{condition}'; limit: '{limit}'; last: '{last}'"


def get_document_by_objectid(args, user_dict, mongo_collection):

    obj_id = args.get('obj_id')
    if not obj_id:
        raise Exception(util.gen_msg("No obj_id passed."))

    try:
        id1 = bson.objectid.ObjectId(obj_id)
    except Exception as e:
        raise Exception(util.gen_msg("obj_id '{obj_id}' not valid: {e}"))

    condition = {'_id': id1}
    cursor = mongo_collection.find(condition)
    if cursor.count() != 1:
        raise Exception(util.gen_msg(f"{cursor.count()} records match {condition}.\n"))

    records_list = get_permitted_records_list(user_dict, cursor)
    if len(records_list) != 1:
        raise Exception(util.gen_msg(
            f"You do not have permission to retrieve record w/ object_id '{obj_id}'"
        ))

    doc = records_list[0]
    doc['_id'] = str(doc.get('_id'))

    return json.dumps(doc)


def get_last_document(args, user_dict, mongo_collection):

    cursor = mongo_collection.find().sort("_id", pymongo.DESCENDING)

    if cursor.count() == 0:
        raise Exception(util.gen_msg(f"No records in collection.\n"))

    doc = cursor[0]
    doc['_id'] = str(doc.get('_id'))

    return json.dumps(doc)


