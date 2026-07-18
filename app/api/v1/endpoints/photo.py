import os
import shutil
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.database.deps import get_db, get_current_user
from app.models.user import User
from app.models.family import FamilyMember
from app.models.photo import Album, Photo
from app.schemas.photo import AlbumCreate, AlbumResponse, PhotoResponse

router = APIRouter(prefix="/albums", tags=["Albums & Photos"])

UPLOAD_DIR = os.path.join("static", "photos")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_user_space_id(db: Session, user_id: int) -> int:
    member = db.query(FamilyMember).filter(FamilyMember.user_id == user_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not part of any family space"
        )
    return member.space_id


@router.get("/", response_model=List[AlbumResponse])
def get_albums(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    albums = db.query(Album).filter(Album.space_id == space_id).all()
    return albums


@router.post("/", response_model=AlbumResponse, status_code=status.HTTP_201_CREATED)
def create_album(
    payload: AlbumCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    db_album = Album(
        space_id=space_id,
        name=payload.name,
        description=payload.description,
        created_by=current_user.id
    )
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album


@router.post("/{album_id}/photos", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
def upload_photo(
    album_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    album = db.query(Album).filter(Album.id == album_id, Album.space_id == space_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found in family space"
        )

    # Generate a unique name and save file locally (Firebase placeholder)
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # local placeholder serving URL
    file_url = f"/static/photos/{unique_filename}"

    db_photo = Photo(
        album_id=album_id,
        file_path=file_url,
        uploaded_by=current_user.id
    )
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_album(
    album_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    album = db.query(Album).filter(Album.id == album_id, Album.space_id == space_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found"
        )

    # Delete actual files
    for photo in album.photos:
        filename = os.path.basename(photo.file_path)
        local_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception:
                pass

    db.delete(album)
    db.commit()
    return None
