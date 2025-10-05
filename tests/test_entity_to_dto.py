import pytest
from pydantic import BaseModel
from dataclasses import dataclass
from dataclasses import asdict

from src.entitydtoconverter.converters import entity_to_dto, entity_to_dtos

from typing import Literal


# TEST CLASSES

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


# FIXTURES

@pytest.fixture
def person_entity_instance():
    """Fixture providing a PersonEntity instance"""
    return PersonEntity(first_name="John", age=25)


@pytest.fixture
def person_dto_instance():
    """Fixture providing a PersonDTO instance"""
    return PersonDTO(first_name="Jane", age=30)


@pytest.fixture
def person_with_gender_entity_instance():
    """Fixture providing a PersonWithGenderEntity instance"""
    gender = GenderEntity(gender="male")
    return PersonWithGenderEntity(first_name="Alice", age=28, gender=gender)


@pytest.fixture
def person_with_gender_dto_instance():
    """Fixture providing a PersonWithGenderDTO instance"""
    gender = GenderDTO(gender="female")
    return PersonWithGenderDTO(first_name="Bob", age=32, gender=gender)


@pytest.fixture
def person_entity_list():
    """Fixture providing a list of PersonEntity instances"""
    return [
        PersonEntity(first_name="Alice", age=25),
        PersonEntity(first_name="Bob", age=30),
        PersonEntity(first_name="Charlie", age=35)
    ]


@pytest.fixture
def person_dto_list():
    """Fixture providing a list of PersonDTO instances"""
    return [
        PersonDTO(first_name="David", age=40),
        PersonDTO(first_name="Eve", age=45)
    ]


@pytest.fixture
def person_entity_with_optional_instance():
    """Fixture providing PersonEntityWithOptional instance with some None values"""
    return PersonEntityWithOptional(
        first_name="Test",
        age=None,
        email="test@example.com"
    )


@pytest.fixture
def person_entity_with_complex_fields_instance():
    """Fixture providing PersonEntityWithComplexFields instance"""
    return PersonEntityWithComplexFields(
        first_name="Complex",
        hobbies=["reading", "coding", "gaming"],
        metadata={"level": "expert", "status": "active"}
    )


class Test_Entity2DTO:

    def test_simple_entity_to_dto_conversion(self, person_entity_instance):
        """Test basic entity to DTO conversion"""
        dto = entity_to_dto(person_entity_instance, PersonDTO)

        assert dto.first_name == person_entity_instance.first_name
        assert dto.age == person_entity_instance.age
        assert isinstance(dto, PersonDTO)

    def test_dto_to_entity_roundtrip(self, person_entity_instance):
        """Test that entity -> DTO -> entity maintains data integrity"""
        # Convert entity to DTO
        dto = entity_to_dto(person_entity_instance, PersonDTO)

        # Convert back to entity
        entity_again = PersonEntity(**dto.model_dump())

        assert entity_again.first_name == person_entity_instance.first_name
        assert entity_again.age == person_entity_instance.age

    def test_entity_to_dto_with_nested_objects(self, person_with_gender_entity_instance):
        """Test entity to DTO conversion with nested objects"""
        dto = entity_to_dto(person_with_gender_entity_instance, PersonWithGenderDTO)

        assert dto.first_name == person_with_gender_entity_instance.first_name
        assert dto.age == person_with_gender_entity_instance.age
        assert dto.gender.gender == person_with_gender_entity_instance.gender.gender

    def test_entity_to_dtos_multiple_conversion(self, person_entity_list):
        """Test converting multiple entities to DTOs"""
        dtos = entity_to_dtos(person_entity_list, PersonDTO)

        assert len(dtos) == len(person_entity_list)
        for i, (entity, dto) in enumerate(zip(person_entity_list, dtos)):
            assert dto.first_name == entity.first_name
            assert dto.age == entity.age
            assert isinstance(dto, PersonDTO)

    def test_entity_to_dtos_empty_list(self):
        """Test converting empty list of entities"""
        dtos = entity_to_dtos([], PersonDTO)
        assert dtos == []

    def test_entity_to_dto_with_optional_fields(self, person_entity_with_optional_instance):
        """Test conversion with optional/None fields"""
        dto = entity_to_dto(person_entity_with_optional_instance, PersonDTOWithOptional)

        assert dto.first_name == person_entity_with_optional_instance.first_name
        assert dto.age == person_entity_with_optional_instance.age  # None
        assert dto.email == person_entity_with_optional_instance.email

    def test_entity_to_dto_with_complex_fields(self, person_entity_with_complex_fields_instance):
        """Test conversion with complex field types (lists, dicts)"""
        dto = entity_to_dto(person_entity_with_complex_fields_instance, PersonDTOWithComplexFields)

        assert dto.first_name == person_entity_with_complex_fields_instance.first_name
        assert dto.hobbies == person_entity_with_complex_fields_instance.hobbies
        assert dto.metadata == person_entity_with_complex_fields_instance.metadata

    def test_entity_to_dto_validation_error(self):
        """Test that invalid data raises ValidationError"""
        # Test that non-dataclass entities raise TypeError
        with pytest.raises(TypeError):
            entity_to_dto("not a dataclass", PersonDTO)