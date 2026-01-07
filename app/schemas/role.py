from pydantic import BaseModel

class RoleCreate(BaseModel):
    name: str
    description: str | None = None

class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {
        "from_attributes": True
    }
