from api_client import InvenioRDMClient
from pathlib import Path
from rocrate_datacite_conversion import ROCrateDataCiteConverter


test_record = {
  "access": {
    "record": "public",
    "files": "public"
  },
  "files": {
    "enabled": True
  },
  "metadata": {
    "creators": [
      {
        "PersonOrOrg": {
          "family_name": "Renkin",
          "given_name": "Moritz",
          "identifiers": [
            {"scheme": "orcid", "identifier": "0000-0002-1404-857X"}
          ],
          "name": "Collins, Thomas",
          "type": "personal"
        },
        "affiliations": [
          {
            "id": "01ggx4157",
            "name": "Entity One"
          }
        ]
      }
    ],
    "publication_date": "2020-06-01",
    "resource_type": { "id": "text" },
    "publisher": "InvenioRDM",
    "title": "A Romans story",
  }
}

file_path = Path(__file__).parent.resolve()

def main():
    upload_dir = file_path / "../test/sample-rocrates/b97348a7-991f-46cf-9834-cf602bacf800/"
    rocrate_metadata_path = upload_dir / "ro-crate-metadata.json"
    client = InvenioRDMClient()
    converter = ROCrateDataCiteConverter()
    upload_files = [upload_dir / filename for filename in converter.get_rocrate_file_paths(rocrate_metadata_path)]

    record_json = converter.generate_datacite_record(rocrate_metadata_path)
    record_id = client.create_draft(record_json)
    client.upload_draft_files(record_id=record_id, file_paths=[upload_dir / "sketch.JPG"])

if __name__ == '__main__':
    main()
