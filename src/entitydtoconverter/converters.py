from dataclasses import asdict, fields, is_dataclass, replace
from typing import Any, List, Literal, Mapping, Optional, Type, TypeVar
from rest_framework.request import Request

from collections.abc import Callable
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


from pydantic import BaseModel
from .base_dto import BaseDTO

# Custom exceptions


class NotValidModelPassed(Exception):
    pass


# DTO types
D = TypeVar("D", bound=BaseDTO)

# Entities type
E = TypeVar("E")

# ADD YOURS
BY_FILTER = Literal["username", "id", "email"]

ADAPTER_MAPPING = Optional[
    Mapping[str, Callable[..., Any]]
]

ENTITY_FIELD_MAPPING = Optional[
    dict[str, str]
]


def request_to_dto(req: Request, dto_model: Type[D]) -> D:
    """
        Given a django/DRF Request, convert it to dto.

        ex:
            req.data = {username="johndoe", email="johndoe@gmail.com"}
            url?username=johndoe&email=johndoe@gmail.com
             \/
            User(username="johndoe", email="johndoe@gmail.com")

        Attention: Make sure the from_attributes is enabled in you DTO pydantic model

        Raises :
         ValidationError
    """

    if req.data:
        data = req.data
    else:
        # FallBack
        data = req.query_params

    return dto_model(
        **{
            k: data.get(k)

            for k in dto_model.model_fields.keys()
        }
    )


def entity_to_dto(entity_instance: E, dto_cls: Type[D]) -> D:
    """

    Convert a dataclass entity (dataclass) to dto (pydantic model).

    Raises:
        ValidationError
    """
    if not is_dataclass(entity_instance):
        raise TypeError(
            f"entity_instance must be a dataclass, got {type(entity_instance)}")
    return dto_cls.model_validate(asdict(entity_instance))


def entity_to_dtos(entities_instances: List[E], dto_cls: Type[D]) -> List[D]:
    return [entity_to_dto(entity_instance, dto_cls) for entity_instance in entities_instances]


def dto_to_entity(dto_instance: BaseDTO, entity_cls: Type[E], field_map: Optional[dict[str, Type[E]]] = None) -> E:

    data = dto_instance.model_dump(exclude_unset=True, exclude_none=True)

    if field_map:
        for field, adapter in field_map.items():
            if is_dataclass(adapter):
                data[field] = dto_to_entity(
                    getattr(dto_instance, field), adapter)
            else:
                raise TypeError(
                    f"Field : {field} is not a valid DTO, instead: {type(field)} : type: {adapter}")

    return entity_cls(**data)


def dto_to_entities(dto_instances: List[D], entity_cls: Type[E], ) -> List[E]:
    return [entity_cls(**dto_instance.model_dump()) for dto_instance in dto_instances]


def update_entity(base_entity: E, update_entity: E) -> E:
    if not is_dataclass(base_entity) or not is_dataclass(update_entity):
        raise TypeError(
            "base_entity e update_entity must be dataclass objects")

    patch = {k: v for k, v in asdict(update_entity).items() if v is not None}

    return replace(base_entity, **patch)


def model_to_entity(model_instance: models.Model,
                    entity_cls: type[E],
                    field_mapping: ENTITY_FIELD_MAPPING = None,
                    adapters: ADAPTER_MAPPING = None,
                    ) -> E:
    """
    Given a model and a entity (dataclass object) return an instance from
    the provided entity

    field_mapping : {
        entity_field_name : db_field_name
    }

    adapters : {
        db_field_name : function to manage this field
    }

    """
    # TODO test this
    entity_ = {}
    field_mapping = field_mapping or {}
    adapters = adapters or {}

    # Check if model_obj is not a Model subclass from django
    if not issubclass(model_instance.__class__, models.Model):
        raise NotValidModelPassed(
            f"Provided instance of model isnt a BaseModel subclass, details: input_type={type(model_instance)} input_value={str(model_instance)}, repr={repr(model_instance)}")

    for field in fields(entity_cls):

        entity_name = field.name
        model_name = field_mapping.get(entity_name, entity_name)

        entity_[entity_name] = getattr(
            model_instance, model_name if model_name != entity_name else entity_name)

        adapter = adapters.get(model_name)

        if adapter:
            entity_[entity_name] = adapter(entity_[entity_name])

    return entity_cls(**entity_)


def get_by(
        model_cls: Type[models.Model],
        filter_field: BY_FILTER,
        filter_value: str,
        entity_cls: Type[E],
        *,
        return_raw=False,
        field_mapping: ENTITY_FIELD_MAPPING = None,
        adapters: ADAPTER_MAPPING = None
) -> E | models.Model | None:
    """
        Get a converted entity from the provided model get from the ORM

        model_cls: the ORM model class
        filter_field: the search field name
        filter_value: the value to filter
        entity_cls: your actual dataclass entity class

        return_raw: whether to return raw data or not
        field_mapping: alias for fields, for example
        adapters: adapters

    """
    try:
        instance = model_cls.objects.get(**{filter_field: filter_value})

        if return_raw:
            return instance

        return model_to_entity(
            model_instance=instance,
            entity_cls=entity_cls,
            adapters=adapters,
            field_mapping=field_mapping
        )
    except ObjectDoesNotExist:
        return None


def get_raw_by(
        model_cls: Type[models.Model],
        filter_field: BY_FILTER,
        filter_value: str,
) -> E | models.Model | None:
    try:
        return model_cls.objects.get(**{filter_field: filter_value})
    except ObjectDoesNotExist:
        return None


def m2m_to_entities(entity_cls: Type[E], remap=None, field_map=None):
    """
    Ease way to convert a M2M field into entities for example:

    return [
        model_to_entity(
                professional,
                ProfessionalEntity,
                field_mapping={"service_categories": "categories"},
                adapters={
                    "categories": helpers.m2m_to_entities(ServiceCategoryEntity)
                }
            )

            for professional in Professional.objects.all()
        ]


    This function will receive a m2m relatedManager in model_to_entity adapter logic.

    Its similiar to use field_map in dto_to_entity but this time, automatically
        
    """
    def _innner(manager):
        return [
            model_to_entity(model_instance=model_instance,
                            entity_cls=entity_cls, field_mapping=remap, adapters=field_map)

            for model_instance in manager.all()]

    return _innner
