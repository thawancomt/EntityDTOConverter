import pytest
from dataclasses import dataclass

from src.entitydtoconverter.converters import update_entity


class Test_Update_Entity:
    def test_update_entity_basic(self):
        """Test updating an entity with another entity"""

        @dataclass
        class PersonEntity:
            first_name: str
            age: int
            email: str | None = None

        base = PersonEntity(first_name="John", age=25,
                            email="john@example.com")
        # email=None should be ignored
        update = PersonEntity(first_name="Jane", age=30, email=None)

        result = update_entity(base, update)

        assert result.first_name == "Jane"  # Updated
        assert result.age == 30  # Updated
        assert result.email == "john@example.com"  # Not updated because None

    def test_update_entity_with_none_values(self):
        """Test that None values in update_entity are ignored"""

        @dataclass
        class PersonEntity:
            first_name: str
            age: int | None = None

        base = PersonEntity(first_name="John", age=25)
        update = PersonEntity(first_name="Jane", age=None)

        result = update_entity(base, update)

        assert result.first_name == "Jane"
        assert result.age == 25  # None should be ignored

    def test_update_entity_invalid_type(self):
        """Test that update_entity raises TypeError for non-dataclass"""
        @dataclass
        class PersonEntity:
            first_name: str
            age: int | None = None

        with pytest.raises(TypeError):
            update_entity("not a dataclass", PersonEntity(
                first_name="test", age=20))
