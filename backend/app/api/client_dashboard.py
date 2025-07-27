from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import date
from sqlalchemy import func

from app.db import models, database
from app.api import deps
from app.services.flussonic import FlussonicService
from requests.exceptions import RequestException



router = APIRouter()

class StreamInfo(BaseModel):
    name: str
    server_id: int
    server_name: str
    # Add other relevant stream info here later, like a preview URL

@router.get("/my-streams", response_model=List[StreamInfo])
def get_my_streams(db: Session = Depends(database.get_db), current_user: models.User = Depends(deps.get_current_user)):
    """
    Retrieves the list of streams assigned to the currently authenticated user.
    """
    user_streams = db.query(models.UserStream).filter(models.UserStream.user_id == current_user.id).all()
    
    if not user_streams:
        return []

    # Enrich stream info with server details
    result = []
    for user_stream in user_streams:
        server = db.query(models.FlussonicServer).filter(models.FlussonicServer.id == user_stream.server_id).first()
        if server:
            result.append(StreamInfo(
                name=user_stream.stream_name,
                server_id=server.id,
                server_name=server.name
            ))
            
    return result

# Endpoints for traffic data and push management will be added here.

class TrafficRecord(BaseModel):
    timestamp: date
    bytes_used: int

    class Config:
        orm_mode = True


@router.get("/{stream_name}/traffic", response_model=List[TrafficRecord])
def get_stream_traffic(
    stream_name: str,
    start_date: date,
    end_date: date,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Retrieves aggregated daily traffic usage data for a specific stream within a date range.
    """
    # Verify the user has access to this stream.
    user_stream = (
        db.query(models.UserStream)
        .filter(
            models.UserStream.user_id == current_user.id,
            models.UserStream.stream_name == stream_name,
        )
        .first()
    )

    if not user_stream:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this stream.",
        )

    # Fetch and aggregate traffic data from the database for the given stream and date range.
    traffic_records = (
        db.query(
            func.date(models.TrafficUsage.timestamp).label("timestamp"),
            func.sum(models.TrafficUsage.bytes_used).label("bytes_used"),
        )
        .filter(
            models.TrafficUsage.stream_name == stream_name,
            models.TrafficUsage.server_id == user_stream.server_id,
            func.date(models.TrafficUsage.timestamp) >= start_date,
            func.date(models.TrafficUsage.timestamp) <= end_date,
        )
        .group_by(func.date(models.TrafficUsage.timestamp))
        .order_by(func.date(models.TrafficUsage.timestamp).asc())
        .all()
    )

    return traffic_records


class PushConfig(BaseModel):
    url: str

class PushCreate(BaseModel):
    url: str

@router.get("/{stream_name}/pushes", response_model=List[PushConfig])
def get_stream_pushes(
    stream_name: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Retrieves the list of push configurations for a stream.
    """
    user_stream = (
        db.query(models.UserStream)
        .filter(
            models.UserStream.user_id == current_user.id,
            models.UserStream.stream_name == stream_name,
        )
        .first()
    )
    if not user_stream:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this stream.",
        )
    server = db.query(models.FlussonicServer).filter(models.FlussonicServer.id == user_stream.server_id).first()
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated server not found.")

    flussonic_service = FlussonicService(server.url, server.username, server.password)
    
    try:
        stream_config = flussonic_service.get_stream_config(stream_name)
        pushes = stream_config.get('pushes', [])
        return [PushConfig(url=push.get('url')) for push in pushes if push.get('url')]
    except (ValueError, RequestException) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not fetch stream configuration from Flussonic. Error: {e}"
        )

@router.post("/{stream_name}/pushes", status_code=status.HTTP_201_CREATED)
def add_stream_push(
    stream_name: str,
    push_config: PushCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Adds a new push URL to a stream.
    """
    user_stream = (
        db.query(models.UserStream)
        .filter(
            models.UserStream.user_id == current_user.id,
            models.UserStream.stream_name == stream_name,
        )
        .first()
    )
    if not user_stream:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this stream.",
        )
    server = db.query(models.FlussonicServer).filter(models.FlussonicServer.id == user_stream.server_id).first()
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated server not found.")

    flussonic_service = FlussonicService(server.url, server.username, server.password)
    
    try:
        current_config = flussonic_service.get_stream_config(stream_name)
        current_pushes = current_config.get('pushes', [])
        
        if any(p.get('url') == push_config.url for p in current_pushes):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This push URL already exists for the stream."
            )

        new_pushes = current_pushes + [{"url": push_config.url}]
        flussonic_service.update_stream_config(stream_name, {"pushes": new_pushes})
        return {"message": "Push configuration added successfully."}
    except (ValueError, RequestException) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not update stream configuration on Flussonic. Error: {e}"
        )

@router.delete("/{stream_name}/pushes", status_code=status.HTTP_200_OK)
def remove_stream_push(
    stream_name: str,
    push_to_delete: PushCreate, # Re-use PushCreate as it has the same structure
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Removes a push URL from a stream.
    """
    user_stream = (
        db.query(models.UserStream)
        .filter(
            models.UserStream.user_id == current_user.id,
            models.UserStream.stream_name == stream_name,
        )
        .first()
    )
    if not user_stream:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this stream.",
        )
    server = db.query(models.FlussonicServer).filter(models.FlussonicServer.id == user_stream.server_id).first()
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated server not found.")

    flussonic_service = FlussonicService(server.url, server.username, server.password)

    try:
        current_config = flussonic_service.get_stream_config(stream_name)
        current_pushes = current_config.get('pushes', [])
        
        updated_pushes = [p for p in current_pushes if p.get('url') != push_to_delete.url]

        if len(updated_pushes) == len(current_pushes):
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Push URL not found in stream configuration."
            )

        flussonic_service.update_stream_config(stream_name, {"pushes": updated_pushes})
        return {"message": "Push configuration removed successfully."}
    except (ValueError, RequestException) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not update stream configuration on Flussonic. Error: {e}"
        )
