from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class TicketBase(BaseModel):
    user_name: str
    category: str
    issue_type: str
    description: str
    context: Optional[str] = None
    priority: Optional[str] = "Medium"

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    severity: Optional[str] = None
    notes: Optional[str] = None

class Ticket(TicketBase):
    id: int
    ticket_id: str
    status: str
    severity: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class EventLogBase(BaseModel):
    actor: str
    action: str
    details: str

class EventLog(EventLogBase):
    id: int
    timestamp: datetime
    ticket_id_fk: int

    class Config:
        orm_mode = True
