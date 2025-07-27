from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import models, database
from pydantic import BaseModel
from typing import List
from app.api import deps
from app.services.flussonic import FlussonicService
from requests.exceptions import RequestException



router = APIRouter()

# Pydantic models for request and response
class ServerBase(BaseModel):
    name: str
    url: str
    username: str
    password: str

class ServerCreate(ServerBase):
    pass

class Server(ServerBase):
    id: int

    class Config:
        orm_mode = True

@router.post("/", response_model=Server, status_code=status.HTTP_201_CREATED)
def create_server(server: ServerCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(deps.get_current_admin_user)):
    # Test connection to Flussonic server before saving
    try:
        flussonic_service = FlussonicService(
            server_url=server.url,
            username=server.username,
            password=server.password
        )
        # A simple call to test credentials and connectivity.
        # This will raise an exception if it fails.
        flussonic_service.get_streams()
    except (RequestException, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect to Flussonic server. Please check URL and credentials. Error: {e}"
        )

    db_server = models.FlussonicServer(**server.dict())
    db.add(db_server)
    db.commit()
    db.refresh(db_server)
    return db_server


@router.get("/", response_model=List[Server])
def read_servers(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(deps.get_current_admin_user)):

    servers = db.query(models.FlussonicServer).offset(skip).limit(limit).all()
    return servers


@router.get("/{server_id}/streams", response_model=List[dict])
def get_server_streams(server_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(deps.get_current_admin_user)):
    """
    Retrieves a list of media streams from a specific Flussonic server.
    """
    db_server = db.query(models.FlussonicServer).filter(models.FlussonicServer.id == server_id).first()
    if not db_server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")

    try:
        flussonic_service = FlussonicService(
            server_url=db_server.url,
            username=db_server.username,
            password=db_server.password
        )
        streams = flussonic_service.get_streams()
        return streams
    except (RequestException, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not fetch streams from Flussonic server. Error: {e}"
        )
