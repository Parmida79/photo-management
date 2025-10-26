from pydantic import BaseModel

from app.utils.helpers import convert_to_camel


class BaseSerializer(BaseModel):
    class Config:
        alias_generator = convert_to_camel
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        use_enum_values = True
        orm_mode = True
        extra = 'allow'

