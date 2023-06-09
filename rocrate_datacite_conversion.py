from rocrate.rocrate import ROCrate
from pathlib import Path
import json
from datacite_schema import Identifier, Agent, Affiliation, PersonOrOrg
from idutils import detect_identifier_schemes, normalize_pid
from urllib.parse import urlparse


file_path = Path(__file__).parent.resolve()

class ROCrateDataCiteConverter:

    supported_creator_identifiers = {"orcid", "gnd", "isni", "ror"}

    def __init__(self, rocrate_metadata_path: str | Path, access_defaults: dict, metadata_defaults: dict):
        rocrate_metadata_path = Path(rocrate_metadata_path)
        with rocrate_metadata_path.open(mode="r") as file:
            self.crate_metadata_raw = json.load(file)
        self.crate = ROCrate(rocrate_metadata_path.parent)

        self.upload_filenames = tuple(self._get_rocrate_filenames())

        self.TEMPLATE_DATACITE_RECORD = {
            "access": access_defaults,
            "metadata": {
                "resource_type": {"id": metadata_defaults["resource_type"]},
                "publisher": metadata_defaults["publisher"]
            }
        }

    def _get_creators(self, creator_emails) -> list[Agent]:
        """
        Reads creators from raw metadata json file, due to lacking functionality in ROCrate package.
        :param creator_emails: Emails of the agents as iterable.
        :return: List of creators.
        """
        creators_by_id = {}
        entities_raw = self.crate_metadata_raw["@graph"]
        agents = [e for e in entities_raw if e.get("@type") == "agent"]

        for agent in agents:
            if agent.get("email") in creator_emails:
                agent_url = agent.get("@id") # @id field contains URL in crates from ROHub
                identifier = self._url2creator_identifier(agent_url)
                identifiers = [identifier] if identifier else None
                person_or_org = PersonOrOrg(identifiers=identifiers)
                creators_by_id[agent_url] = Agent(person_or_org=person_or_org)

        #if len(creators_by_id) == 0:
         #   creator_email = next(iter(creator_emails))
          #  creators_by_id[creator_email] = Agent(person_or_org=PersonOrOrg(identifiers=[self._url2creator_identifier(creator_email)]))

        for agent in agents:
            agent_name = agent.get("name")
            agent_url = agent.get("@id")
            agent_affiliation = agent.get("affiliation")
            if agent_url in creators_by_id:
                creator = creators_by_id[agent_url]
                if agent_name is not None:
                    creator.person_or_org.given_name, creator.person_or_org.family_name = agent_name.rsplit(" ") # TODO document name split
                if agent_affiliation is not None:
                    creator.affiliations = [Affiliation(name=agent_affiliation)]

        return list(creators_by_id.values())

    def generate_datacite_record(self) -> dict:
        """
        TODO docu
        :return:
        """
        record = self.TEMPLATE_DATACITE_RECORD.copy()

        record['files'] = {"enabled": (len(self.upload_filenames) != 0)}

        record_metadata: dict[str, type | list] = record['metadata']
        record_metadata['title'] = self.crate.name
        if self.crate.description is not None and self.crate.description != "nan":
            record_metadata['description'] = self.crate.description
        record_metadata['publication_date'] = self.crate.datePublished.strftime('%Y-%m-%d')

        # rocrate keywords is a comma separated string of https://schema.org/keywords
        # https://www.researchobject.org/ro-crate/1.1/contextual-entities.html#subjects--keywords
        # crate.keywords is already split into array but may contain uris
        if self.crate.keywords is not None and self.crate.keywords != "nan":
            record_metadata['subjects'] = [{'subject': keyword} for keyword in self.crate.keywords]

        # In practice creators are an array of email strings instead of the proper object.
        # https://github.com/ResearchObject/ro-crate/blob/c4b4e3e0936c95406e4adc82bcb7b1025c05a786/docs/1.1/workflows.md?plain=1#L263
        # https://inveniordm.docs.cern.ch/reference/metadata/#creators-1-n
        # agents = [e for e in crate.contextual_entities if e.type == "agent"]
        creator_emails: set[str] = {creator for e in self.crate.get_entities() if e.get("creator") for creator in e.get("creator")}
        creators = self._get_creators(creator_emails)
        record_metadata["creators"] = [c.to_dict() for c in creators]

        # In practice contributors are urls instead of the proper object
        # https://github.com/ResearchObject/ro-crate/blob/c4b4e3e0936c95406e4adc82bcb7b1025c05a786/docs/profiles.md?plain=1#L193
        # e.get('contributors') is an array that is not mentioned in the documentation

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

        # https://www.researchobject.org/ro-crate/1.1/metadata.html#recommended-identifiers
        # https://inveniordm.docs.cern.ch/reference/metadata/#alternate-identifiers-0-n
        record_metadata['identifiers'] = [
            self._url2identifier(e.get('identifier')).to_dict()
            for e in self.crate.get_entities() if e.get('identifier') and e.get('@id') == './'
        ]

        # In practice related identifiers are frequently stored in @id and @type might be an
        # identifier as well. Furthermore, inveniordm has no wildcard relation_type.
        # The limited list of well documented types cannot be simply mapped to relation_type.
        # https://github.com/inveniosoftware/invenio-rdm-records/blob/master/invenio_rdm_records/fixtures/data/vocabularies/relation_types.yaml
        # The citation property could be added here as well
        # https://www.researchobject.org/ro-crate/1.1/contextual-entities.html#publications-via-citation-property
        # record_metadata['related_identifiers'] = [
        #     dict(url2identifier(e.get('identifier')), **{'relation_type': {
        #         id: 'ispartof' if e.get('@type') == 'Dataset' else 'cites'
        #     }})
        #     for e in self.crate.get_entities() if e.get('identifier') and e.get('@id') != './'
        # ]

        self.crate_metadata_raw = None
        self.crate = None
        return record

    def _get_rocrate_filenames(self) -> list[str]:
        # external links contain '//' and will not be uploaded
        return [
            e.get('name')
            for e in self.crate.get_entities()
            if e.get('@type') and 'File' in e.get('@type') and '//' not in e.get('name')
        ]


    @staticmethod
    def _url2creator_identifier(url: str) -> Identifier | None:
        """
        Convert the url into a creator identifier object, if scheme is supported
        :param url: Creator ID URL
        :return: Identifier object if scheme is supported for creators, None else.
        """
        ident = ROCrateDataCiteConverter._url2identifier(url)
        scheme = ident.scheme
        if scheme in ROCrateDataCiteConverter.supported_creator_identifiers:
            return ident
        return None


    @staticmethod
    def _url2identifier(url: str) -> Identifier:
        scheme = detect_identifier_schemes(url)
        if scheme:
            scheme = scheme[0]
            identifier = normalize_pid(url, scheme)
        else:
            scheme = 'other'
            identifier = url
        if scheme == 'url':
            # unfortunately idutils (used by inveniordm) does not support w3id and geonames
            parsed = urlparse(url)
            if parsed.hostname.endswith('w3id.org'):
                scheme = 'w3id'
                identifier = parsed.path[1:]
            if parsed.hostname.endswith('geonames.org'):
                scheme = 'geonames'
                identifier = parsed.path[1:]
        return Identifier(identifier=identifier, scheme=scheme)
