from api_client import InvenioRDMClient
from pathlib import Path
from rocrate_datacite_conversion import ROCrateDataCiteConverter
from configparser import ConfigParser


file_path = Path(__file__).parent.resolve()

config = ConfigParser()
config.read(file_path / "config.ini")
config = {s: dict(config.items(s)) for s in config.sections()}


def main():
    upload_dir = Path(config["rocrate"]["rocrate_path"])
    rocrate_metadata_path = upload_dir / "ro-crate-metadata.json"
    client = InvenioRDMClient(base_url=config["api"]["base_url"], token=config["api"]["bearer_token"])
    converter = ROCrateDataCiteConverter(rocrate_metadata_path,
                                         access_defaults=config["access"], metadata_defaults=config["metadata"])
    upload_file_paths = [upload_dir / filename for filename in converter.upload_filenames]

    record_json = converter.generate_datacite_record()
    record_id = client.create_draft(record_json)
    client.upload_draft_files(record_id=record_id, file_paths=upload_file_paths)


if __name__ == '__main__':
    main()
