from rocrate.rocrate import ROCrate
from pathlib import Path
import json
from datacite_schema import Identifier, Agent, Affiliation, PersonOrOrg


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

    def _get_creators(self, creator_emails) -> list[Agent]:
        """
        Reads creators from raw metadata json file, due to lacking functionality in ROCrate package.
        :param creator_emails: Emails of the agents.
        :return: List of creators.
        """
        creators_by_id = {}
        entities_raw = self.crate_metadata_raw["@graph"]
        agents = [e for e in entities_raw if e.get("@type") == "agent"]

        for agent in agents:
            if agent.get("email") in creator_emails:
                agent_id = agent.get("@id")
                identifiers = [Identifier(scheme="Unknown", identifier=agent_id)]
                person_or_org = PersonOrOrg(identifiers=identifiers)
                creators_by_id[agent_id] = Agent(person_or_org=person_or_org)

        for agent in agents:
            # TODO personal vs organizational
            agent_name = agent.get("name")
            agent_id = agent.get("@id")
            agent_affiliation = agent.get("affiliation")
            if agent_id in creators_by_id:
                creator = creators_by_id[agent_id]
                if agent_name is not None:
                    creator.person_or_org.given_name, creator.person_or_org.family_name = agent_name.rsplit(" ")
                if agent_affiliation is not None:
                    creator.affiliations = [Affiliation(id="0", name=agent_affiliation)]

        return list(creators_by_id.values())


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
        record_metadata: dict[str, type | list] = record['metadata']
        record_metadata['title'] = self.crate.name
        record_metadata['description'] = self.crate.description
        record_metadata['publication_date'] = self.crate.datePublished.strftime('%Y-%m-%d')

        # rocrate keywords is a comma separated string of https://schema.org/keywords
        # https://www.researchobject.org/ro-crate/1.1/contextual-entities.html#subjects--keywords
        # crate.keywords is already split into array but may contain uris
        record_metadata['subjects'] = [{'subject': keyword} for keyword in self.crate.keywords]

        # In practice creators are an array of email strings instead of the proper object.
        # https://github.com/ResearchObject/ro-crate/blob/c4b4e3e0936c95406e4adc82bcb7b1025c05a786/docs/1.1/workflows.md?plain=1#L263
        # https://inveniordm.docs.cern.ch/reference/metadata/#creators-1-n
        # agents = [e for e in crate.contextual_entities if e.type == "agent"]
        creator_emails: set[str] = {creator for e in self.crate.get_entities() if e.get("creator") for creator in e.get("creator")}
        creators = self._get_creators(creator_emails)
        record_metadata["creators"] = [c.to_dict() for c in creators]
        # TODO contributers (how to map roles?)

        # Technically a license should be an object with a link in the property @id
        # https://www.researchobject.org/ro-crate/1.1/contextual-entities.html#licensing-access-control-and-copyright
        # In practice it is a string equivalent to the Identifier value
        # https://inveniordm.docs.cern.ch/reference/metadata/#rights-licenses-0-n
        # the documentation uses lower case
        licenses: set[str] = {e.get('license') for e in self.crate.get_entities() if e.get('license')}
        record_metadata['rights'] = [{'id': license.lower()} for license in licenses]
    
        # https://www.researchobject.org/ro-crate/1.1/contextual-entities.html#time
        # https://inveniordm.docs.cern.ch/reference/metadata/#dates-0-n
        # "Only id needs to be passed on the REST API."
        record_metadata['dates'] = [
            {'date': e.get('temporalCoverage'), 'type': {'id': 'other'}}
            for e in self.crate.get_entities() if e.get('temporalCoverage')
        ]

        self.crate_metadata_raw = None
        self.crate = None
        return record


if __name__ == '__main__':
    file_path = Path(__file__).parent.resolve()
    rocrate_path = file_path / '../test/sample-rocrates/b97348a7-991f-46cf-9834-cf602bacf800/ro-crate-metadata.json'
    ROCrateDataCiteConverter().generate_datacite_record(rocrate_path)
