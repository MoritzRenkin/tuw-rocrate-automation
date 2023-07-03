from rocrate.rocrate import ROCrate
from pathlib import Path


def get_datacite_record_from_rocrate(rocrate_path: str | Path) -> dict:
    """
    TODO docu
    :param rocrate_path:
    :return:
    """
    rocrate_path = Path(rocrate_path)
    crate = ROCrate(rocrate_path)
    pass


if __name__ == '__main__':
    file_path = Path(__file__).parent.resolve()
    rocrate_path = file_path / '../test/sample-rocrates/b97348a7-991f-46cf-9834-cf602bacf800.zip'
    get_datacite_record_from_rocrate(rocrate_path)