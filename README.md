# tuw-rocrate-automation

Convert RO-Crate (Research Object Crate)[^1] InvenioRDM's bibliographic records and upload it to a RDM (Research Data Management) instance.

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


### Setup

- Create personal API token for the TU Wien Research Data API at https://test.researchdata.tuwien.ac.at/account/settings/applications/ (Test instance)

- Install Python dependencies:
```sh
python -m pip install -r requirements.txt
```

### Basic Usage
```sh
python tuw_rocrate_upload.py -h
usage: TUW RDM RO-Crate Upload [-h] [-u URL] [-t TOKEN] [-p] path                                                                                     
                                                                                                                                                      
Deposit your RO-Crate metadata and referenced files into the TU Wien Research Data Repository.                                                                                  
                                                                                                                                                      
positional arguments:                                                                                                                                 
  path                  Relative or absolute path to directory containing ro-crate.metadata.json file. Referenced files must be in the same directory.
                                                                                                                                                      
options:                                                                                                                                              
  -h, --help              show this help message and exit                                                                                               
  -u URL, --url URL       URL to the RDM API                                                                                                            
  -t TOKEN, --token       Bearer token for API authentication                                                                                           
  -p, --publish           Publish the drafted record on the RDM Repository
  ```

Some arguments have fallback default values stored in `config.ini`.

[^1]: The script assumes the RO-Crate schema used by [RoHub](https://reliance.rohub.org/)