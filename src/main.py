from api_client import ApiClient

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
          "family_name": "Brown",
          "given_name": "Troy",
          "type": "personal"
        }
      },
      {
        "person_or_org": {
          "family_name": "Collins",
          "given_name": "Thomas",
          "identifiers": [
            {"scheme": "orcid", "identifier": "0000-0002-1825-0097"}
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
    "resource_type": { "id": "image" },
    "title": "A Romans story",
  }
}

def main():
    client = ApiClient()
    #records = client.get_all_records()
    record_id = client.create_draft(test_record)
    client.upload_draft_files(record_id=record_id, file_paths=["src/testfile.txt"])
    client.publish_draft(record_id)

if __name__ == '__main__':
    main()
