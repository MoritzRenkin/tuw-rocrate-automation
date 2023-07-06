from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod



class AbstractJsonSchema(ABC):
    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}

    #def __str__(self):
     #   self.to_dict()


@dataclass
class Identifier(AbstractJsonSchema):
    scheme: str
    identifier: str


@dataclass
class Affiliation(AbstractJsonSchema):
    id: str
    name: str


@dataclass
class PersonOrOrg(AbstractJsonSchema):
    given_name: str = None
    family_name: str = None
    identifiers: list[Identifier] = None
    name: str = None # if type is organizational
    type: str = "personal"

    def to_dict(self) -> dict:
        if not all([self.given_name, self.family_name, self.identifiers]):
            raise ValueError()
        return super().to_dict()


@dataclass
class Agent(AbstractJsonSchema):
    person_or_org : PersonOrOrg
    affiliations: list[str] = None # if type is personal
    role: str = "unknown" # TODO

    def to_dict(self) -> dict:
        if not all([self.affiliations]):
            raise ValueError()
        return super().to_dict()