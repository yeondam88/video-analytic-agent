from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.summary_service import SummaryService

router = APIRouter()

@router.get("/videos/{video_id}/summary")
def get_video_summary(video_id: int, db: Session = Depends(get_db)):
    # TODO: Implement video summary retrieval
    return {"message": "Summary endpoint not implemented yet"}

@router.post("/videos/{video_id}/summary")
async def generate_video_summary(
    video_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate a new summary for a video."""
    try:
        summary_service = SummaryService(db)
        summary = await summary_service.generate_summary(video_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 