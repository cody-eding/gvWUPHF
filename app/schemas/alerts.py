from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# Define the nested model for tagged_users
class TaggedUser(BaseModel):
    name: str
    id: str  # Assuming 'id' is a string (e.g., an email address)

# Define the Severity Enum
class Severity(Enum):
    ok = "ok"
    info = "info"
    warning = "warning"
    critical = "critical"

class Alert(BaseModel):
    queue_id: int = Field(description="The unique identifier of the queue to which the alert belongs")
    title: str = Field(description="The title of the alert", min_length=1)
    message: str = Field(description="The detailed message of the alert. Supports Markdown.", min_length=1)
    severity: Optional[Severity] = Field(None, description="The severity level of the alert (must be one of 'ok', 'info', 'warning', 'critical')")
    url: Optional[str] = Field(None, description="A URL associated with the alert")
    tagged_users: Optional[List[TaggedUser]] = Field(None, description="A list of users to tag in the alert - functionality depends on platform.")

    class Config:
        json_schema_extra = {
            "example": {
                "queue_id": 1,
                "title": "System Alert",
                "message": "There is an issue with the system.",
                "severity": "critical",
                "url": "https://example.com/alert/1"
            }
        }