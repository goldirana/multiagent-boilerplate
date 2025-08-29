from fastapi import APIRouter, HTTPException
from typing import List, Dict

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/")
async def list_agents():
    """List all available agents"""
    return {"agents": ["chat_agent", "task_agent", "research_agent"]}

@router.post("/{agent_name}/start")
async def start_agent(agent_name: str):
    """Start a specific agent"""
    return {"message": f"Agent {agent_name} started", "status": "success"}
