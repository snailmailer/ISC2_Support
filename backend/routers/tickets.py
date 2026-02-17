from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, database
import datetime
import csv
import io

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)

def generate_ticket_id(db: Session):
    # Format: INC-YYYY-XXXX (e.g., INC-2026-0001)
    year = datetime.datetime.now().year
    count = db.query(models.Ticket).count() + 1
    return f"INC-{year}-{count:04d}"

def classify_ticket(description: str, issue_type: str) -> dict:
    """Simple rule-based AI classification (Mock)"""
    desc_lower = description.lower()
    type_lower = issue_type.lower()
    
    classification = {
        "category": "Incident Report", # Default
        "priority": "Medium"
    }
    
    # Access Request triggers
    if any(x in desc_lower or x in type_lower for x in ["password", "access", "login", "account", "permission", "unlock"]):
        classification["category"] = "Access Request"
        classification["priority"] = "Low"
        
    # Critical triggers
    if any(x in desc_lower or x in type_lower for x in ["down", "crash", "hack", "breach", "urgent", "critical"]):
        classification["priority"] = "High"
        if "server" in desc_lower or "database" in desc_lower:
             classification["priority"] = "Critical"

    return classification

@router.post("/", response_model=schemas.Ticket)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(database.get_db)):
    ticket_id = generate_ticket_id(db)
    
    # Auto-Classification
    auto_class = classify_ticket(ticket.description, ticket.issue_type)
    
    # Use auto-values if not explicitly provided or if we want to override
    # Here we default to the user choice if provided, but let's assume "AI" assists if user picks defaults
    final_category = ticket.category if ticket.category else auto_class["category"]
    
    # If user selected Medium (default) but AI thinks it's Critical, maybe we bump it?
    # For now, let's just stick to the requested simple flow or user input
    # But let's apply the category if it seems mismatched? 
    # Actually, let's just use the user input if valid, but we could return a warning.
    # For this implementation, let's trust the user but log what AI thought?
    # Or better: if the user didn't specify priority (it defaults to Medium), use AI priority.
    final_priority = ticket.priority if ticket.priority != "Medium" else auto_class["priority"]

    db_ticket = models.Ticket(
        ticket_id=ticket_id,
        user_name=ticket.user_name,
        category=final_category,
        issue_type=ticket.issue_type,
        description=ticket.description,
        context=ticket.context,
        priority=final_priority
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    # Log the creation event
    log = models.EventLog(
        ticket_id_fk=db_ticket.id,
        actor="System",
        action="Created",
        details=f"Ticket created by {ticket.user_name}. AI Classification: {auto_class['category']} / {auto_class['priority']}"
    )
    db.add(log)
    db.commit()

    return db_ticket

@router.get("/", response_model=List[schemas.Ticket])
def read_tickets(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Ticket)
    
    if status and status != 'all':
        query = query.filter(models.Ticket.status == status)
    if priority and priority != 'all':
        query = query.filter(models.Ticket.priority == priority)
    if category and category != 'all':
        query = query.filter(models.Ticket.category == category)
        
    tickets = query.offset(skip).limit(limit).all()
    return tickets

@router.get("/export")
def export_tickets(db: Session = Depends(database.get_db)):
    tickets = db.query(models.Ticket).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Ticket ID", "User", "Category", "Issue Type", "Description", "Status", "Priority", "Created At", "Resolved At"])
    
    # Rows
    for t in tickets:
        writer.writerow([
            t.ticket_id, 
            t.user_name, 
            t.category, 
            t.issue_type, 
            t.description, 
            t.status, 
            t.priority, 
            t.created_at, 
            t.resolved_at
        ])
    
    output.seek(0)
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=tickets_export.csv"})

@router.get("/{ticket_id}", response_model=schemas.Ticket)
def read_ticket(ticket_id: str, db: Session = Depends(database.get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.put("/{ticket_id}", response_model=schemas.Ticket)
def update_ticket(ticket_id: str, ticket_update: schemas.TicketUpdate, db: Session = Depends(database.get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Status Update Logic with timestamp
    if ticket_update.status:
        # Check if closing
        if ticket_update.status in ["Resolved", "Closed"] and ticket.status not in ["Resolved", "Closed"]:
            ticket.resolved_at = datetime.datetime.utcnow()
        # Check if reopening
        if ticket_update.status in ["Open", "In Progress"] and ticket.status in ["Resolved", "Closed"]:
            ticket.resolved_at = None
            
        ticket.status = ticket_update.status

    if ticket_update.priority:
        ticket.priority = ticket_update.priority
    if ticket_update.severity:
        ticket.severity = ticket_update.severity
    
    db.commit()
    db.refresh(ticket)
    
    # Log the update
    log = models.EventLog(
        ticket_id_fk=ticket.id,
        actor="Admin", # Mocked
        action="Updated",
        details=f"Status: {ticket.status}, Priority: {ticket.priority}"
    )
    db.add(log)
    db.commit()
    
    return ticket
