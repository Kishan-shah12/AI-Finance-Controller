from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.agent.llm import AgentService

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])
agent_service = AgentService()

class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

@router.post("/query")
def process_agent_query(req: QueryRequest, db: Session = Depends(get_db)):
    result = agent_service.process_query(req.query, db, req.context)
    
    if result.get("status") == "AGENT_UNAVAILABLE":
        return result
        
    if result.get("status") == "ERROR":
        raise HTTPException(status_code=500, detail=result.get("message"))
        
    return result
