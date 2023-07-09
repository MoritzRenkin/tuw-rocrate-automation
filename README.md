# tuw-rocrate-automation

Convert RO-Crate (Research Object Crate) from RoHub to InvenioRDM's bibliographic records and upload it to a RDM (Research Data Management) instance.

## Supported metadata
Due to the structure of rocrates not all relevant fields can be extracted. Some fields are provided via config. Other information is not partly extracted because one required field has no wildcard value. Reasons and links to related documentation is provided in the corresponding place in the code.

* ~~resource_type~~ (via config)
* creators
* title
* publication_date
* ~~additional_titles~~
* description
* ~~additional_descriptions~~
* rights
* ~~contributors~~
* subjects
* ~~languages~~
* dates
* ~~version~~
* ~~publisher~~ (via config)
* identifiers
* ~~related_identifiers~~
* ~~funding~~

Removed fields that are not part of the deposit page yet.


## Setup

- Create personal API token for the TU Wien Research Data API at https://test.researchdata.tuwien.ac.at/account/settings/applications/

- Paste the created token into tuw-rocrate-automation/api-access-token.txt

- Install Python dependencies:
```shell
python -m pip install -r requirements.txt
```

## Execute
```shell
python tuw_rocrate_upload.py
  [-token string]  # token for RDM
  [-rdm url]  # url to RDM
  [-path string]  # path to a directory containing a ro-crate-metadata.json file
```
All values have fallback value in config or in case of path it is the folder of execution.


## 

TODOs:
- ~~remove identifier for Creator if unsupported scheme~~
- ~~config.ini inkl token~~
- CL Parameter
- Readme.md
- ~~File paths~~
- Github Release
- Add orcid in zenodo
- TuWel