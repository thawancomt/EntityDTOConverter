
from pydantic import BaseModel
from pydantic.config import ConfigDict


# This model_config is required to work in some function
class BaseDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        revalidate_instances='always',
        validate_assignment=True,
        extra='forbid',
        str_strip_whitespace=True
    )
