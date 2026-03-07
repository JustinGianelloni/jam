from pydantic import BaseModel, Field


class Application(BaseModel):
    id: str
    active: bool
    display_label: str = Field(alias="displayLabel")
