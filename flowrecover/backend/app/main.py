from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, customers, dashboard, leaks, predictions, ai, prevention, recovery, upload
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FlowRecover API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all route modules
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(customers.router, prefix="/customers", tags=["customers"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(leaks.router, prefix="/leaks", tags=["leaks"])
app.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
app.include_router(prevention.router, prefix="/prevention", tags=["prevention"])
app.include_router(recovery.router, prefix="/recovery", tags=["recovery"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
