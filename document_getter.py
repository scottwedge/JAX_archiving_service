## global imports:

import pymongo
import bson.objectid

## local imports:

import config
import util


def get_permitted_records_list(user_dict, cursor):

    records = []

    if user_dict.get('admin'): 
        for record in cursor:
            records.append(record)
        return records

    user_groups_list = user_dict.get('groups_list')
    if not isinstance(user_groups_list, list):
        raise Exception(util.gen_msg(
            f"user_dict['groups_list'] '{user_groups_list}' is not a list; user_dict: '{user_dict}'"
        ))

    for record in cursor:
        if 'system_groups' not in record:
            util.log_email(util.gen_msg(
                f"record has no system_groups key; record: '{record}'"
            ))
            continue
        allowed_groups_list = record.get('system_groups')
        if not isinstance(allowed_groups_list, list):
            util.log_email(util.gen_msg(
                f"record['groups_list'] '{allowed_groups_list}' is not a list; record: '{record}'"
            ))
        for group in allowed_groups_list:
            if group in user_groups_list:
                records.append(record)
                break

    return records


def get_documents(args, user_dict, mongo_collection):
    return user_dict


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

    return doc


def get_last_document(args, user_dict, mongo_collection):

    cursor = mongo_collection.find().sort("_id", pymongo.DESCENDING)

    if cursor.count() == 0:
        raise Exception(util.gen_msg(f"No records in collection.\n"))

    doc = cursor[0]
    doc['_id'] = str(doc.get('_id'))

    return doc


