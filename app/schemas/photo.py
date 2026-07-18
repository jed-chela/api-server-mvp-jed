from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.schemas.user import UserResponse


class PhotoBase(BaseModel):
    file_path: str


class PhotoCreate(PhotoBase):
    uploaded_by: Optional[int] = None


class PhotoResponse(PhotoBase):
    id: int
    album_id: int
    uploaded_by: Optional[int] = None
    uploaded_at: datetime
    uploader: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class AlbumBase(BaseModel):
    name: str
    description: Optional[str] = None


class AlbumCreate(AlbumBase):
    pass


class AlbumResponse(AlbumBase):
    id: int
    space_id: int
    created_by: Optional[int] = None
    created_at: datetime
    creator: Optional[UserResponse] = None
    photos: List[PhotoResponse] = []

    class Config:
        from_attributes = True
