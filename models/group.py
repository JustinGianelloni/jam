from pydantic import BaseModel


class Group(BaseModel):
    id: str
    name: str
    type: str
    description: str | None = None
