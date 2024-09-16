from pydantic import BaseModel


class ConfiguredBaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        extra = "forbid"
