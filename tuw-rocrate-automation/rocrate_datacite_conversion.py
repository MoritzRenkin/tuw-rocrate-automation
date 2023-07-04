from rocrate.rocrate import ROCrate
from pathlib import Path

TEMPLATE_DATACITE_RECORD = {
    "access": {
        "record": "public",
        "files": "public"
    },
    "files": {
        "enabled": True
    },
    "metadata": {}
}


def generate_datacite_record(rocrate_path: str | Path) -> dict:
    """
    TODO docu
    :param rocrate_path:
    :return:
    """
    rocrate_path = Path(rocrate_path)
    crate = ROCrate(rocrate_path)

    record = TEMPLATE_DATACITE_RECORD.copy()
    record_metadata = record['metadata']
    record_metadata['title'] = crate.name
    record_metadata['description'] = crate.description
    record_metadata['publication_date'] = crate.datePublished.strftime('%Y-%m-%d')

    record_metadata['subjects'] = list(map(lambda keyword: {"subject": keyword}, crate.keywords))

    creator_emails = {creator for e in crate.get_entities() if e.get("creator") for creator in e.get("creator")}
    # TODO


    return record


if __name__ == '__main__':
    file_path = Path(__file__).parent.resolve()
    rocrate_path = file_path / '../test/sample-rocrates/b97348a7-991f-46cf-9834-cf602bacf800'
    generate_datacite_record(rocrate_path)
