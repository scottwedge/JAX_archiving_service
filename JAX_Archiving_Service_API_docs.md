# JAX Archiving Service 

[![N|Solid](https://clic-ctsa.org/sites/default/files/styles/large/public/2019-10/jacksonLabLogo.png)](https://jacksonlaboratory.sharepoint.com/sites/ResearchIT)

# API Documentation

## Endpoints

- [`/archive`][1]
- [`/retrieve`][2]
- [`/get_collection`][3]
- [`/archive_failed`][4]
- [`archive_processing`][5]
- [`/archive_submitted`][6]
- [`/archive_success`][7]
- [`/retrieve_failed`][8]
- [`/retrieve_processing`][9]
- [`/retrieve_submitted`][10]
- [`/retrieve_success`][11]

---
### /archive
This endpoint will accept a valid `POST` archiving request as described below. The successful return for this endpoint is the object id of the metadata in mongoDB. A successful return means your request was successfully submitted to pbs and further updates on the status of the archiving event will be directed by pbs via this archiving microservice.

An unsuccessful return value will be a string (starting with `ERROR:`) describing why the request was not submitted to pbs.

The body of the `POST` request must contain the following keys [`api_key`, `metadata`, `source_folder`, `service_path`]
- `api_key`
-- Value is the string representing the key
- `metadata`
-- Value is a dictionary containing some required keys. Described in more detail below [click here][metadata_link].
- `source_folder`
-- String representing the absolute path to the directory requested to be archived
- `service_path`
-- Not applicable for requests to archive `faculty` data
-- Applicable for any of the services. Presently there are only two services archiving data (single cell & microscopy)
--The user specified path in the archive after `/archive/services/<singlecell or microscopy>/`
-- The service will generate the correct prefix with the appropriate service name `singlecell` or `microscopy`

##### `metadata`
A dictionary with the following required keys [`manager_user_id`, `user_id`, `project_name`, `grant_id`, `notes`, `system_groups`, `request_type`]
-   `manager_user_id` The short username of the principal investigator (PI) owning the data.
-   `user_id` The short username of the person who generated the data. In many cases this is a postdoc. It can be the PI. 
-   `project_name` The name of the project the user specifies that the data is associated with.
-   `grant_id` The grant ID associated with the data. If there is no grant ID, set this to the empty string. The service will recognize the empty string and enter “None_entered_by_user” into mongoDB.
-   `notes` Any string the user might find useful for locating these archived files at a later date.
-   *** `system_groups`*** A list in the form of an array of the HPC group(s) that will own the data and/or have permission to access the data on the cluster.
-   `request_type` A string corresponding to the type of data requesting to be archived [`faculty`, `GT`, `singlecell`, `microscopy`].

#### Example request

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
        "request_type": "singlecell"
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
---
---

#### Example article excerpt

> The overriding design goal for Markdown's
> formatting syntax is to make it as readable
> as possible. The idea is that a
> Markdown-formatted document should be
> publishable as-is, as plain text, without
> looking like it's been marked up with tags
> or formatting instructions.


| Example | Table |
| ------ | ------ |
| Dropbox | [plugins/dropbox/README.md][PlDb] |
| GitHub | [plugins/github/README.md][PlGh] |
| Google Drive | [plugins/googledrive/README.md][PlGd] |
| OneDrive | [plugins/onedrive/README.md][PlOd] |
| Medium | [plugins/medium/README.md][PlMe] |
| Google Analytics | [plugins/googleanalytics/README.md][PlGa] |



[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)


   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>
   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>

[1]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#archive
[2]: https://www.google.com
[3]: https://www.google.com
[4]: https://www.google.com
[5]: https://www.google.com
[6]: https://www.google.com
[7]: https://www.google.com
[8]: https://www.google.com
[9]: https://www.google.com
[10]: https://www.google.com
[11]: https://www.google.com
[metadata_link]: https://github.com/TheJacksonLaboratory/JAX_archiving_service/blob/frank/JAX_Archiving_Service_API_docs.md#metadata