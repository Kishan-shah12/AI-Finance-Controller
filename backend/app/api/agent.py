import time
from collections import defaultdict
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.agent.llm import AgentService

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])
agent_service = AgentService()

# In-memory sliding window rate limiter
_request_history = defaultdict(list)
RATE_LIMIT_WINDOW = 60 # 60 seconds
MAX_REQUESTS_PER_WINDOW = 30

def check_rate_limit(client_id: str):
    now = time.time()
    _request_history[client_id] = [t for t in _request_history[client_id] if now - t < RATE_LIMIT_WINDOW]
    if len(_request_history[client_id]) >= MAX_REQUESTS_PER_WINDOW:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait a moment before sending more queries.")
    _request_history[client_id].append(now)

class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

@router.post("/query")
def process_agent_query(req: QueryRequest, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)
    
    result = agent_service.process_query(req.query, db, req.context)
    
    if result.get("status") == "AGENT_UNAVAILABLE":
        return result
        
    if result.get("status") == "ERROR":
        raise HTTPException(status_code=500, detail=result.get("message"))
        
    return result
