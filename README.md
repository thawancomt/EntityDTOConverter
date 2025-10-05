# EntityDTOConverter

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Domain-Driven Design (DDD) utility library that simplifies the interaction between **dataclass entities** and **Pydantic DTOs** in Python applications. Designed specifically for Django/DRF projects, it bridges the gap between your domain layer (entities) and your presentation/infrastructure layers (DTOs), making data conversion seamless and type-safe.

## 🎯 Purpose

In DDD architecture, it's crucial to separate concerns:
- **Entities (dataclasses)**: Your domain models in the business logic layer
- **DTOs (Pydantic models)**: Data Transfer Objects for API requests/responses and database interactions

This library provides bidirectional conversion utilities to maintain clean architecture boundaries while minimizing boilerplate code.

## 🚀 Features

- ✅ **Entity ↔ DTO Conversion**: Seamless bidirectional conversion between dataclasses and Pydantic models
- ✅ **Nested Object Support**: Handle complex nested structures with field mapping
- ✅ **Django ORM Integration**: Convert Django models to entities with custom field mappings and adapters
- ✅ **Request to DTO**: Direct conversion from Django/DRF requests to DTOs
- ✅ **Entity Updates**: Smart entity updates that ignore `None` values
- ✅ **Batch Operations**: Convert lists of entities/DTOs efficiently
- ✅ **Many-to-Many Support**: Built-in helpers for Django M2M relationships
- ✅ **Type Safe**: Full type hints and validation using Pydantic
- ✅ **Extensible**: Custom adapters and field mappings for complex scenarios

## 📦 Installation

```bash
pip install entitydtoconverter
```

Or using `uv`:
```bash
uv add entitydtoconverter
```

## 📋 Requirements

- Python 3.13+
- Django 5.2.7+
- Django REST Framework 3.16.1+
- Pydantic 2.11.10+

## 🔧 Quick Start

### Basic Setup

```python
from dataclasses import dataclass
from pydantic import BaseModel
from entitydtoconverter.converters import dto_to_entity, entity_to_dto

# Define your domain entity (dataclass)
@dataclass
class UserEntity:
    username: str
    email: str
    age: int

# Define your DTO (Pydantic model)
class UserDTO(BaseModel):
    username: str
    email: str
    age: int
```

### DTO to Entity Conversion

```python
# Convert DTO to Entity
user_dto = UserDTO(username="johndoe", email="john@example.com", age=30)
user_entity = dto_to_entity(user_dto, UserEntity)

print(user_entity)
# UserEntity(username='johndoe', email='john@example.com', age=30)
```

### Entity to DTO Conversion

```python
# Convert Entity to DTO
user_entity = UserEntity(username="janedoe", email="jane@example.com", age=25)
user_dto = entity_to_dto(user_entity, UserDTO)

print(user_dto)
# UserDTO(username='janedoe', email='jane@example.com', age=25)
```

## 🔥 Advanced Usage

### Nested Objects with Field Mapping

```python
from typing import Literal

@dataclass
class AddressEntity:
    street: str
    city: str
    country: str

@dataclass
class PersonEntity:
    name: str
    age: int
    address: AddressEntity

class AddressDTO(BaseModel):
    street: str
    city: str
    country: str

class PersonDTO(BaseModel):
    name: str
    age: int
    address: AddressDTO

# Convert with nested objects
address_dto = AddressDTO(street="123 Main St", city="NYC", country="USA")
person_dto = PersonDTO(name="John", age=30, address=address_dto)

# Use field_map to specify nested conversions
person_entity = dto_to_entity(
    person_dto, 
    PersonEntity, 
    field_map={"address": AddressEntity}
)
```

### Django Request to DTO

```python
from rest_framework.request import Request
from entitydtoconverter.converters import request_to_dto

class CreateUserDTO(BaseModel):
    username: str
    email: str
    password: str

def create_user_view(request: Request):
    # Automatically extract and validate request data
    user_dto = request_to_dto(request, CreateUserDTO)
    # ... handle user creation
```

### Django Model to Entity Conversion

```python
from django.db import models
from entitydtoconverter.converters import model_to_entity

# Django Model
class UserModel(models.Model):
    username = models.CharField(max_length=100)
    email_address = models.EmailField()  # Note: different field name
    age = models.IntegerField()

# Domain Entity
@dataclass
class UserEntity:
    username: str
    email: str  # Different name from model
    age: int

# Convert with field mapping
user_model = UserModel.objects.get(id=1)
user_entity = model_to_entity(
    user_model,
    UserEntity,
    field_mapping={
        "email": "email_address"  # Map entity field to model field
    }
)
```

### Custom Adapters for Complex Fields

```python
from datetime import datetime
from entitydtoconverter.converters import model_to_entity

@dataclass
class PostEntity:
    title: str
    created_at: str  # We want ISO format string

class PostModel(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField()

# Custom adapter to format datetime
def format_datetime(dt: datetime) -> str:
    return dt.isoformat()

post_model = PostModel.objects.get(id=1)
post_entity = model_to_entity(
    post_model,
    PostEntity,
    adapters={
        "created_at": format_datetime
    }
)
```

### Batch Conversions

```python
from entitydtoconverter.converters import dto_to_entities, entity_to_dtos

# Convert multiple DTOs to entities
user_dtos = [
    UserDTO(username="user1", email="user1@example.com", age=20),
    UserDTO(username="user2", email="user2@example.com", age=25),
]
user_entities = dto_to_entities(user_dtos, UserEntity)

# Convert multiple entities to DTOs
entities = [
    UserEntity(username="user3", email="user3@example.com", age=30),
    UserEntity(username="user4", email="user4@example.com", age=35),
]
dtos = entity_to_dtos(entities, UserDTO)
```

### Entity Updates

```python
from entitydtoconverter.converters import update_entity

# Base entity
base_user = UserEntity(username="johndoe", email="john@example.com", age=30)

# Update data (None values are ignored)
update_data = UserEntity(username="johndoe_updated", email=None, age=None)

# Apply update (only non-None values are updated)
updated_user = update_entity(base_user, update_data)
print(updated_user)
# UserEntity(username='johndoe_updated', email='john@example.com', age=30)
```

### Many-to-Many Relationships

```python
from entitydtoconverter.converters import m2m_to_entities

@dataclass
class TagEntity:
    name: str
    slug: str

class TagModel(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField()

class PostModel(models.Model):
    title = models.CharField(max_length=200)
    tags = models.ManyToManyField(TagModel)

# Convert M2M relationships
post = PostModel.objects.get(id=1)
tag_converter = m2m_to_entities(TagEntity)
tag_entities = tag_converter(post.tags)
```

### Query by Field with Conversion

```python
from entitydtoconverter.converters import get_by

# Fetch and convert in one step
user_entity = get_by(
    model_cls=UserModel,
    filter_field="username",  # Can be "username", "id", or "email"
    filter_value="johndoe",
    entity_cls=UserEntity,
    field_mapping={"email": "email_address"}
)

if user_entity:
    print(f"Found user: {user_entity.username}")
else:
    print("User not found")
```

## 📚 API Reference

### Core Functions

#### `dto_to_entity(dto_instance, entity_cls, field_map=None)`
Convert a Pydantic DTO to a dataclass entity.

**Parameters:**
- `dto_instance`: Pydantic model instance
- `entity_cls`: Target dataclass class
- `field_map`: Optional dict mapping field names to nested entity classes

**Returns:** Entity instance

---

#### `entity_to_dto(entity_instance, dto_cls)`
Convert a dataclass entity to a Pydantic DTO.

**Parameters:**
- `entity_instance`: Dataclass instance
- `dto_cls`: Target Pydantic model class

**Returns:** DTO instance

**Raises:** `TypeError` if entity_instance is not a dataclass

---

#### `dto_to_entities(dto_instances, entity_cls)`
Convert a list of DTOs to entities.

---

#### `entity_to_dtos(entities_instances, dto_cls)`
Convert a list of entities to DTOs.

---

#### `update_entity(base_entity, update_entity)`
Update an entity with non-None values from another entity.

**Parameters:**
- `base_entity`: Original entity
- `update_entity`: Entity with update values

**Returns:** New entity instance with updates applied

---

#### `model_to_entity(model_instance, entity_cls, field_mapping=None, adapters=None)`
Convert a Django model instance to an entity. if model has many to many field use field_mapping

**Parameters:**
- `model_instance`: Django model instance
- `entity_cls`: Target entity class
- `field_mapping`: Dict mapping entity field names to model field names
- `adapters`: Dict mapping field names to adapter functions

---

#### `request_to_dto(req, dto_model)`
Convert Django/DRF request to DTO.

**Parameters:**
- `req`: Django Request object
- `dto_model`: Target DTO class

**Returns:** DTO instance with validated data

---

#### `get_by(model_cls, filter_field, filter_value, entity_cls, return_raw=False, field_mapping=None, adapters=None)`
Fetch and convert a Django model to entity.

**Parameters:**
- `model_cls`: Django model class
- `filter_field`: Field to filter by ("username", "id", or "email")
- `filter_value`: Value to search for
- `entity_cls`: Target entity class
- `return_raw`: If True, return raw model instead of entity
- `field_mapping`: Optional field mappings
- `adapters`: Optional field adapters

**Returns:** Entity instance or None if not found

---

#### `m2m_to_entities(entity_cls, remap=None, field_map=None)`
Create a converter function for many-to-many relationships.

**Parameters:**
- `entity_cls`: Target entity class
- `remap`: Optional field remapping
- `field_map`: Optional field adapters

**Returns:** Converter function for M2M manager

## 🏗️ Architecture & Use Cases

### Clean Architecture with DDD

```
┌─────────────────────────────────────────────────────┐
│                  Presentation Layer                  │
│              (Views, Serializers, DTOs)             │
│                    ↕ (DTOs)                         │
└─────────────────────────────────────────────────────┘
                       ↕
            EntityDTOConverter 
                       ↕
┌─────────────────────────────────────────────────────┐
│                   Domain Layer                       │
│              (Entities, Business Logic)             │
│                  ↕ (Entities)                       │
└─────────────────────────────────────────────────────┘
                       ↕
            EntityDTOConverter
                       ↕
┌─────────────────────────────────────────────────────┐
│              Infrastructure Layer                    │
│              (Database, ORM, Models)                │
└─────────────────────────────────────────────────────┘
```

### Common Use Cases

1. **API Request Handling**: Convert incoming API requests to validated DTOs, then to domain entities
2. **Database Persistence**: Convert entities to Django models before saving
3. **API Response**: Convert entities to DTOs for JSON serialization
4. **Service Layer**: Keep business logic clean by working with entities while adapters handle conversions
5. **Testing**: Easily mock data with dataclasses without Django ORM dependencies

## 🧪 Testing

The library comes with comprehensive test coverage. Run tests with:

```bash
pytest tests/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👤 Author

**thawancomt**
- Email: thawancomt@gmail.com
- GitHub: [@thawancomt](https://github.com/thawancomt)

## 🙏 Acknowledgments

- Built for Django and DRF developers who value clean architecture
- Inspired by Domain-Driven Design principles
- Powered by Pydantic for robust data validation

---

**Made with ❤️ for the Python DDD community**
