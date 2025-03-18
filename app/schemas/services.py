from pydantic import BaseModel

class Service(BaseModel):
    name: str
    id: int
    type: str
    recipient: str