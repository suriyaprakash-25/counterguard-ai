from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.engine import get_db_session
from backend.database.repositories.graph_repo import GraphRepository
from backend.services.graph_service import GraphService

router = APIRouter(prefix="/graph")


def get_graph_service(session: Session = Depends(get_db_session)) -> GraphService:
    repo = GraphRepository(session)
    return GraphService(repo)


@router.get("/data")
def get_data(service: GraphService = Depends(get_graph_service)):
    return {"data": service.get_data()}


@router.get("/stats")
def get_stats(service: GraphService = Depends(get_graph_service)):
    return {"data": service.get_stats()}


@router.get("/nodes/{node_id}")
def get_node_details(node_id: str, service: GraphService = Depends(get_graph_service)):
    node = service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    return {"data": node}
