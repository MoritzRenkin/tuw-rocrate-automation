from api_client import InvenioRDMClient, APIResponseException
from pathlib import Path
from rocrate_datacite_conversion import ROCrateDataCiteConverter
from configparser import ConfigParser
import argparse

file_path = Path(__file__).parent.resolve()

config = ConfigParser()
config.read(file_path / "config.ini")
config = {s: dict(config.items(s)) for s in config.sections()}


def upload_crate(rocrate_path: Path, token: str|None, url: str|None, publish: bool=False):
    if not token:
        token = config["api"]["bearer_token"]
        assert token != "", "You have not provided a bearer token for the API authentication."
    if not url:
        url = config["api"]["base_url"]
        assert url != "", "You have not provided a URL to the RDM API."

    rocrate_metadata_path = rocrate_path / "ro-crate-metadata.json"
    client = InvenioRDMClient(base_url=url, token=token)
    converter = ROCrateDataCiteConverter(rocrate_metadata_path,
                                         access_defaults=config["access"], metadata_defaults=config["metadata"])
    upload_file_paths = [rocrate_path / filename for filename in converter.upload_filenames]

    record_json = converter.generate_datacite_record()
    record_id = client.create_draft(record_json)
    client.upload_draft_files(record_id=record_id, file_paths=upload_file_paths)

    print(f"Draft Record with ID {record_id} was created. You can now edit and publish it in the \"My Dashboard\" section of the TUW Research Data Web portal.")
    if publish:
        try:
            client.publish_draft(record_id)
            print(f"Record with ID {record_id} was published.")
        except APIResponseException as e:
            print(f"Draft Record with ID {record_id} could not be published because some mandatory fields could not be filled using the provided RO-Crate.")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="TUW RDM RO-Crate Upload",
        description="Deposit your rocrate data into the TU Wien Research Data Repository.")
    parser.add_argument("path", type=Path, help="Relative or absolute path to directory containing ro-crate.metadata.json file. Referenced files must be in the same directory.")
    parser.add_argument("-u", "--url", type=str, help="URL to the RDM API")
    parser.add_argument("-t", "--token", type=str, help="Bearer token for API authentication")
    parser.add_argument("-p", "--publish", action="store_true", help="Publish the drafted record on the RDM Repository")
    args = parser.parse_args()


    upload_crate(rocrate_path=args.path, url=args.url, token=args.token, publish=args.publish)
