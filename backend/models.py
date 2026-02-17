import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, unique=True, index=True) # NIST friendly ID e.g., INC-2026-001
    user_name = Column(String, index=True)
    category = Column(String) # Access Request or Incident Report
    issue_type = Column(String) # e.g., Password reset, System error
    description = Column(Text)
    context = Column(Text) # How did it happen?
    status = Column(String, default="Open") # Open, In Progress, Resolved, Closed
    priority = Column(String, default="Medium") # Low, Medium, High, Critical
    severity = Column(String, nullable=True) # NIST severity
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    logs = relationship("EventLog", back_populates="ticket")

class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id_fk = Column(Integer, ForeignKey("tickets.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    actor = Column(String) # System, Admin, User
    action = Column(String) # Created, Updated, Commented
    details = Column(Text)

    ticket = relationship("Ticket", back_populates="logs")
