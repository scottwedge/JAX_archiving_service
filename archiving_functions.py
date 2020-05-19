import config
import datetime as dt
import flask
import json
import os
import requests
import time

from bson.objectid import ObjectId
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from jsonschema import validate
from typing import Optional


def build_archived_path_faculty(pi, submitter, project):
    today = str(dt.date.today())
    # PREFIX allows for easy testing
    archived_path = (
        f"/archive/faculty/{pi.lower()}-lab/{submitter.lower()}/{today}/{project}"
    )
    return archived_path


def validate_service_path(service_path):
    while service_path[0] == "/":
        service_path = service_path[1:]
    test_list = ["archive", "service", "singlecell", "microscopy", "gt"]
    fields = service_path.split("/")
    for field in fields:
        for to_test in test_list:
            if to_test in field.lower():
                # When this function is called it should be in a try/except
                # so that the following string will be returned to user.
                raise Exception(
                    f"service_path: {service_path} is malformed. Cannot include {field}."
                )
    return service_path


def build_archived_path_services(service_name: str, service_path: str):
    if service_name != "gt":
        try:
            service_path = validate_service_path(service_path)
        except:
            return f"The following error occured when validating service_path: {e}"
        service_path = Path(service_path)
        for parent in service_path.parents:
            # test if 'service' will match as a substring
            # When this function is called it should be in a try/except
            # so that the following string will be returned to user.
            if parent.match(f"*/{{services,archive,{service_name}}}*"):
                raise Exception("invalid service_path")
        archived_path = f"{app.config['PREFIX']}/services/{service_name}/{service_path}"
    else:
        tail_path_fields = service_path.split("/")[3:]
        tail_path = "/".join(tail_path_fields)
        # year = str(datetime.date.today()).split("-")[0]
        year = service_path.split("/")[4][0:4]
        archived_path = f"/archive/GT/{year}/{tail_path}"
    return archived_path


def completion_notification_body(
    action, source_path, destination_path, user, status=True
):
    email_content = {
        "subject": f"{user['fname'].capitalize()}, notice of your {action} request status"
    }
    email_content["body"] = (
        f"Hi {user['fname'].capitalize()},\nYour request to {action} {source_path} has "
        f"{'completed successfully' if status else 'failed'}.\n"
    )
    if status:
        if action == "archive":
            email_content["body"] = (
                email_content["body"]
                + f"\nYour files were deposited in the archive at {destination_path}"
            )
        else:
            delete_date_raw = dt.date.today() + timedelta(days=30)
            fmt = "%B %d, %Y"
            delete_date = delete_date_raw.strftime(fmt)

            email_content["body"] = (
                email_content["body"]
                + f"\nYour retrieved files are waiting for you at {destination_path}\n"
                "Please be sure to access and retrieve your files before "
                + str(delete_date)
                + " at which time they will autodelete from fastscratch.\n"
                + "Once you retriveve your files from fastscratch to your working "
                + "directory, you should delete your files from fastscratch."
            )
    return email_content


def processing_notification_body(action, source_path, user):
    email_content = {
        "subject": f"{user['fname'].capitalize()}, notice of your {action} request status"
    }

    email_content["body"] = (
        f"Hi {user['fname'].capitalize()},\nYour request to {action} {source_path} "
        + "is now leaving the queue and is beginning to process. "
        + f"You will receive another email when this {action} request completes."
    )
    return email_content
