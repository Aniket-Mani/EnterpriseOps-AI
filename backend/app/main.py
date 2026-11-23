from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from app.config import settings
from app.db.session import engine
from app.api.routes.tasks import router as tasks_router
from app.api.routes.approvals import router as approvals_router

app = FastAPI(
    title = settings.app_name,
    description="Multi agent autonomous enterprise operations platform",
    version="0.1.0",
)
app.include_router(tasks_router)
app.include_router(approvals_router)

@app.get('/')
def root():
    return{
        "message":"EnterpriseOps AI API is running",
        "status" : "healthy",
    }

@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return{
            "status":"healthy",
            "database":"connected",
        }
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "status":"unhealthy",
                "database":"disconnected",
            }
        )