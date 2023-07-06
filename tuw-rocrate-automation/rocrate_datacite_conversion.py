from rocrate.rocrate import ROCrate
from pathlib import Path
import json

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

class ROCrateDataCiteConverter:

    def __init__(self):
        self.crate_metadata_raw: dict = {}
        self.crate: ROCrate | None = None

    def _get_creator_names(self, creator_emails) -> list[str]:
        """
        Reads creator names from raw metadata file, due to lacking functionality in ROCrate package.
        :param creator_emails: Emails of the agents.
        :return:
        """
        creator_ids = set()
        creator_names = []
        entities_raw = self.crate_metadata_raw["@graph"]
        agents = [e for e in entities_raw if e.get("@type") == "agent"]

        for agent in agents:
            if agent.get("email") in creator_emails:
                creator_ids.add(agent.get("@id"))

        for agent in agents:
            agent_name = agent.get("@name")
            if agent.get("@id") in creator_ids and agent_name is not None:
                creator_names.append(agent_name)




        return creator_names
    def generate_datacite_record(self, rocrate_metadata_path: str | Path) -> dict:
        """
        TODO docu
        :return:
        """
        rocrate_metadata_path = Path(rocrate_metadata_path)
        with rocrate_metadata_path.open(mode="r") as file:
            self.crate_metadata_raw = json.load(file)
        self.crate = ROCrate(rocrate_metadata_path.parent)

        record = TEMPLATE_DATACITE_RECORD.copy()
        record_metadata = record['metadata']
        record_metadata['title'] = self.crate.name
        record_metadata['description'] = self.crate.description
        record_metadata['publication_date'] = self.crate.datePublished.strftime('%Y-%m-%d')

        record_metadata['subjects'] = list(map(lambda keyword: {"subject": keyword}, self.crate.keywords))

        # agents = [e for e in crate.contextual_entities if e.type == "agent"]
        creator_emails: set[str] = {creator for e in self.crate.get_entities() if e.get("creator") for creator in e.get("creator")}
        creator_names = self._get_creator_names(creator_emails)
        pass
        # TODO

        self.crate_metadata_raw = None
        self.crate = None
        return record


if __name__ == '__main__':
    file_path = Path(__file__).parent.resolve()
    rocrate_path = file_path / '../test/sample-rocrates/b97348a7-991f-46cf-9834-cf602bacf800/ro-crate-metadata.json'
    ROCrateDataCiteConverter().generate_datacite_record(rocrate_path)
