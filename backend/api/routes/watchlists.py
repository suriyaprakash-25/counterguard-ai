"""
watchlists.py — Phase 3: Watchlist Management REST API Routes
FastAPI endpoints for watchlist CRUD operations across 8 entity categories, pause/resume, and export.
"""
from typing import List

from fastapi import APIRouter, HTTPException, Response

from backend.schemas.watchlist import WatchlistCreateRequest, WatchlistItemDTO
from backend.services.watchlist_manager import watchlist_manager

router = APIRouter(prefix="/watchlists", tags=["Watchlist Management"])


@router.get("", response_model=List[WatchlistItemDTO])
async def get_all_watchlists():
    """Fetch all active and paused watchlists across 8 target entity categories."""
    return watchlist_manager.get_all_watchlists()


@router.post("", response_model=WatchlistItemDTO)
async def create_watchlist_item(request: WatchlistCreateRequest):
    """Create a new watchlist target entry."""
    return watchlist_manager.create_watchlist_item(request)


@router.delete("/{item_id}")
async def delete_watchlist_item(item_id: str):
    """Delete a target entry from watchlists."""
    success = watchlist_manager.delete_watchlist_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Watchlist target not found.")
    return {"message": f"Target '{item_id}' deleted successfully."}


@router.post("/{item_id}/pause", response_model=WatchlistItemDTO)
async def pause_watchlist_item(item_id: str):
    """Pause monitoring for a watchlist target."""
    try:
        return watchlist_manager.pause_watchlist_item(item_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{item_id}/resume", response_model=WatchlistItemDTO)
async def resume_watchlist_item(item_id: str):
    """Resume monitoring for a watchlist target."""
    try:
        return watchlist_manager.resume_watchlist_item(item_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/export")
async def export_watchlists_csv():
    """Export watchlists in CSV format."""
    csv_data = watchlist_manager.export_watchlists_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=CounterGuard_Watchlists.csv"
        },
    )
