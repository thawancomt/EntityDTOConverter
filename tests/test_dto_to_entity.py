import pytest
from pydantic import BaseModel
from dataclasses import dataclass
from dataclasses import asdict

from src.entitydtoconverter.converters import dto_to_entity, dto_to_entities, update_entity

from typing import Literal

# MOCKS

@dataclass
class PersonEntity:
    first_name: str
    age: int


class PersonDTO(BaseModel):
    first_name: str
    age: int


@dataclass
class GenderEntity:
    gender: Literal["male", "female"]


class GenderDTO(BaseModel):
    gender: Literal["male", "female"]


@dataclass
class PersonWithGenderEntity:
    first_name: str
    age: int
    gender: GenderEntity


class PersonWithGenderDTO(BaseModel):
    first_name: str
    age: int
    gender: GenderDTO


@dataclass
class PersonEntityWithOptional:
    first_name: str
    age: int | None = None
    email: str | None = None


class PersonDTOWithOptional(BaseModel):
    first_name: str
    age: int | None = None
    email: str | None = None


@dataclass
class PersonEntityWithComplexFields:
    first_name: str
    hobbies: list[str]
    metadata: dict[str, str]


class PersonDTOWithComplexFields(BaseModel):
    first_name: str
    hobbies: list[str]
    metadata: dict[str, str]


class Test_dto2entity:

    def test_simple_conversor(self):
        data = {
            "first_name": "validname",
            "age": 18
        }

        p1 = PersonDTO(**data)
        e1 = PersonEntity(**data)

        assert dto_to_entity(p1, PersonEntity).first_name == e1.first_name
        assert dto_to_entity(p1, PersonEntity).age == e1.age

    def test_nested_conversor(self):
        g_dto = GenderDTO(gender="male")
        p_dto = PersonWithGenderDTO(first_name="validuser", age=18, gender=g_dto)

        r_en = dto_to_entity(p_dto, PersonWithGenderEntity, field_map={"gender": GenderEntity})

        assert r_en.first_name == p_dto.first_name
        assert r_en.age == p_dto.age
        assert r_en.gender.gender == p_dto.gender.gender

        assert p_dto.model_dump(mode="json") == asdict(r_en)

    def test_dto_to_entities_multiple(self):
        """Test converting multiple DTOs to entities"""
        data1 = {"first_name": "Alice", "age": 25}
        data2 = {"first_name": "Bob", "age": 30}

        dtos = [PersonDTO(**data1), PersonDTO(**data2)]
        entities = dto_to_entities(dtos, PersonEntity)

        assert len(entities) == 2
        assert entities[0].first_name == "Alice"
        assert entities[0].age == 25
        assert entities[1].first_name == "Bob"
        assert entities[1].age == 30

    def test_dto_to_entities_empty_list(self):
        """Test converting empty list of DTOs"""
        entities = dto_to_entities([], PersonEntity)
        assert entities == []

    def test_dto_with_none_values_excluded(self):
        """Test that None values are excluded from conversion"""

        class PersonDTOWithOptional(BaseModel):
            first_name: str
            age: int | None = None
            email: str | None = None

        @dataclass
        class PersonEntityWithOptional:
            first_name: str
            age: int | None = None
            email: str | None = None

        dto = PersonDTOWithOptional(
            first_name="Test", age=None, email="test@example.com")
        entity = dto_to_entity(dto, PersonEntityWithOptional)

        assert entity.first_name == "Test"
        assert entity.age is None  # None values should be excluded
        assert entity.email == "test@example.com"

    def test_dto_with_unset_fields_excluded(self):
        """Test that unset fields are excluded from conversion"""

        class PersonDTOWithOptional(BaseModel):
            first_name: str
            age: int = 18
            email: str | None = None

        @dataclass
        class PersonEntityWithOptional:
            first_name: str
            age: int = 18
            email: str | None = None

        # Create DTO without setting age and email
        dto = PersonDTOWithOptional(first_name="Test")
        entity = dto_to_entity(dto, PersonEntityWithOptional)

        assert entity.first_name == "Test"
        # age and email should not be set since they weren't in the DTO
        assert not hasattr(entity, 'age') or entity.age == 18  # Default value
        assert entity.email is None

    
    def test_dto_to_entity_invalid_field_map(self):
        """Test that invalid field_map raises TypeError"""

        @dataclass
        class AddressEntity:
            street: str

        class AddressDTO(BaseModel):
            street: str

        class PersonWithAddressDTO(BaseModel):
            first_name: str
            age: int
            address: AddressDTO

        dto = PersonWithAddressDTO(
            first_name="Test", age=25, address=AddressDTO(street="123 Main St"))

        # field_map should map to dataclass types, not other types
        with pytest.raises(TypeError):
            dto_to_entity(dto, PersonEntity, field_map={"address": str})

    def test_dto_to_entity_with_list_field(self):
        """Test conversion with list fields"""

        class PersonDTOWithHobbies(BaseModel):
            first_name: str
            hobbies: list[str]

        @dataclass
        class PersonEntityWithHobbies:
            first_name: str
            hobbies: list[str]

        dto = PersonDTOWithHobbies(
            first_name="Test", hobbies=["reading", "coding"])
        entity = dto_to_entity(dto, PersonEntityWithHobbies)

        assert entity.first_name == "Test"
        assert entity.hobbies == ["reading", "coding"]

    def test_dto_to_entity_with_dict_field(self):
        """Test conversion with dict fields"""

        class PersonDTOWithMetadata(BaseModel):
            first_name: str
            metadata: dict[str, str]

        @dataclass
        class PersonEntityWithMetadata:
            first_name: str
            metadata: dict[str, str]

        dto = PersonDTOWithMetadata(
            first_name="Test", metadata={"key": "value"})
        entity = dto_to_entity(dto, PersonEntityWithMetadata)

        assert entity.first_name == "Test"
        assert entity.metadata == {"key": "value"}
