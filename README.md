# tuw-rocrate-automation

Convert RO-Crate (Research Object Crate)[^1] InvenioRDM's bibliographic records and upload it to a RDM (Research Data Management) instance.

### Supported metadata
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

### Potential issues, Implementation challenges

Due to the differing natures of the RO-Crate and DataCite standards, the resulting mapping allows only for a subset of the fields used by the TUW RDM Repository to be filled automatically.
Some metadata fields that cannot be filled automatically, as denoted in section "supported Metadata".


For other fields, certain assumptions had to be made:
- family_name, last_name: DataCite has separate attributes for the given and last name of a creator or other contribter whereas RO-Crate only has a name. In order to fill these two fields in the RDM API, we split the RO-Crate name attribute by spaces and use the last part as the family name with the rest serving as given name.

### Test Upload

We use the RO-Crate from ./test/sample-rocrates/19f2cf29-c1c7-4abc-8443-354e7698bc86/ as a demonstrative upload.
In this case, we directly publish the record using the `--publish` flag. In normal operation, it is advisable to publish manually using the Web Portal after checking the metadata and filling out potentially missing values.
```shell
python tuw_rocrate_upload.py test/sample-rocrates/b97348a7-991f-46cf-9834-cf602bacf800 --token <your-token> --url https://test.researchdata.tuwien.ac.at/api/ --publish
```
If you want to reproduce this test call, replace <your-token> with your personal API token.
The published record is immediately visible in the research data portal, including the files referenced in the RO-Crate: https://test.researchdata.tuwien.ac.at/records/fqgr5-zs043.


[^1]: The script assumes the RO-Crate schema used by [RoHub](https://reliance.rohub.org/)