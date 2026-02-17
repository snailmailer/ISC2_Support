from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import tickets
from .database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NIST 800-61 Ticketing System",
    description="API for Incident Response and Access Requests",
    version="1.0.0"
)

# CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for now (dev mode)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the NIST Ticketing System API"}
