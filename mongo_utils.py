# unconditional global imports:
import urllib.parse
from bson.objectid import ObjectId

# unconditional local imports:
import config

from util import get_timestamp, log_email, scrub_dict_keys

# imports conditional on config:
if config.testing["mongo_on"]:
    import pymongo
else:
    import mocks.pymongo_mock


collection = config.mongo["collection"]


def get_mongo_client():
    try:
        user = urllib.parse.quote_plus(
            config.mongo.get("user")
        )  # percent-escape string
        passwd = urllib.parse.quote_plus(
            config.mongo.get("passwd")
        )  # percent-escape string
        host = config.mongo.get("host")
        port = config.mongo.get("port")
        uri = f"mongodb://{user}:{passwd}@{host}:{port}"
        client_obj = pymongo.MongoClient(uri, authSource=config.mongo.get("authdb"))
        client_obj.admin.command(
            "ismaster"
        )  # tests for client != None and good connection
    except Exception as e:
        log_email(f"ERROR: could not connect to '{host}:{port}': {e}")
        return None

    return client_obj


def get_mongo_collection(
    client_obj=None,
    database_name=config.mongo.get("db"),
    collection_name=config.mongo.get("collection"),
):
    if not isinstance(client_obj, pymongo.mongo_client.MongoClient):
        client_obj = get_mongo_client()
        if not client_obj:
            log_email(f"ERROR: get_mongo_client() failed.")
            return None
    try:
        db_obj = client_obj[database_name]
        collection_obj = db_obj[collection_name]
    except Exception as e:
        log_email(
            f"ERROR: could not connect to collection "
            + f"'{database_name}.{collection_name}': {e}"
        )
        return None

    return collection_obj


def mongo_set(key, val, to_set, collection):
    query = {"_id": ObjectId(val)} if "_id" == key else {key: val}
    result = collection.update_one(query, {"$set": to_set})
    assert result.acknowledged
    return result.modified_count


def mongo_set_unset(key, val, to_set, to_unset, collection):
    query = {"_id": ObjectId(val)} if "_id" == key else {key: val}
    result = collection.update_one(query, {"$set": to_set, "$unset": to_unset})
    assert result.acknowledged
    return result.modified_count


def mongo_delete_doc(key, val, collection):
    query = {"_id": ObjectId(val)} if "_id" == key else {key: val}
    collection.delete_one(query)
    log_email(f"Deleting")
    return


def mongo_ingest(metadata, collection):
    """
    dict must be entire body of post request where one of the top-level
    keys is "metadata" which has for its value a dict containing the
    metadata to ingest
    """
    doc = collection.find_one({"archivedPath": metadata["archivedPath"]})
    try:
        if not doc:
            metadata.update(
                {
                    "when_ready_for_pbs": get_timestamp(),
                    "when_submitted_to_pbs": None,
                    "when_archival_queued": None,
                    "when_archival_started": None,
                    "when_archival_completed": None,
                    "failed_multiple": False,
                }
            )
            metadata = scrub_dict_keys(metadata)
            inserted_id = collection.insert_one(metadata).inserted_id
            log_email(f"Metadata inserted with id: {inserted_id}")
            metadata["_id"] = str(inserted_id)
            return metadata

        elif ("failed" in doc["archival_status"]) and (
            doc["failed_multiple"] is not True
        ):  # failed 1 time previously, allow this 1 retry
            mongo_set(
                "archivedPath",
                metadata["archivedPath"],
                {"archival_status": "ready_for_pbs", "failed_multiple": True},
                collection,
            )

            doc = collection.find_one({"archivedPath": metadata["archivedPath"]})
            return doc

        elif "dry_run" in doc["archival_status"]:  # do nothing, return doc
            return doc

        else:  # already archived and not a dry_run
            msg = f"{metadata['archivedPath']} already in Mongo."
            log_email(msg)
            raise Exception(msg)

    except Exception as e:
        raise Exception(f"Metadata insertion failed with error: {e}")
