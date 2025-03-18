from pydantic import BaseModel, Field
from typing import List

class Queue(BaseModel):
    name: str = Field(description="The name of the queue")
    id: int = Field(description="The unique identifier for the queue")
    service_ids: List[int] = Field(description="A list of service IDs associated with the queue")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "solarwinds",
                "id": 1,
                "service_ids": [1, 2]
            }
        }