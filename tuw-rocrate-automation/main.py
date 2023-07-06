from api_client import InvenioRDMClient
from pathlib import Path

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
        "person_or_org": {
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
    client = InvenioRDMClient()
    records = client.get_all_records()
    record_id = client.create_draft(test_record)
    client.upload_draft_files(record_id=record_id, file_paths=[file_path / "../test/testfile.txt"])
    #client.publish_draft(record_id)

if __name__ == '__main__':
    main()
