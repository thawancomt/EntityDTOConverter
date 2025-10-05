import pytest
from pydantic import BaseModel
from dataclasses import dataclass
from dataclasses import asdict

from src.entitydtoconverter.converters import dto_to_entity

from typing import Literal

# MOCKS


@dataclass
class PersonEntity:
    first_name: str
    age: int


class PersonDTO(BaseModel):
    first_name: str
    age: int


class Test_dto2entity:

    def test_simple_conversor(self):

        data = {
            "first_name" : "validname",
            "age" : 18
        }

        p1 = PersonDTO(
            **data
        )

        e1 = PersonEntity(
            **data
        )

        assert dto_to_entity(p1, PersonEntity).first_name == e1.first_name
        assert dto_to_entity(p1, PersonEntity).age == e1.age

    def test_nested_conversor(self):

        @dataclass
        class GenderEntity:
            gender : Literal["male", "female"]

        @dataclass
        class PersonEntity:
            first_name : str
            age : int
            gender : GenderEntity

        class GenderDTO(BaseModel):
            gender : Literal["male", "female"]

        class PersonDTO(BaseModel):
            first_name : str
            age : int
            gender : GenderDTO

        g_dto = GenderDTO(gender="male")
        p_dto = PersonDTO(first_name="validuser", age=18, gender=g_dto)


        r_en = dto_to_entity(p_dto, PersonEntity, field_map={"gender" : GenderEntity})

        assert r_en.first_name == p_dto.first_name
        assert r_en.age == p_dto.age
        assert r_en.gender.gender == p_dto.gender.gender

        assert p_dto.model_dump(mode="json") == asdict(r_en)