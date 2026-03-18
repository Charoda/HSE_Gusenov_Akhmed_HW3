from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.models import Link, User
from app.schemas import LinkCreate, LinkUpdate, LinkResponse, LinkStats, LinkSearchResponse
from app.services.link_service import LinkService
from app.utils.redis_client import redis_client
from app.api.auth_router import get_current_user

router = APIRouter(prefix="/links", tags=["links"])


@router.post("/shorten", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
def shorten_url(
    link_data: LinkCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    try:
        link, _ = LinkService.create_link(db, link_data, user_id)
        return link
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{short_code}")
def redirect_to_original(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    link = LinkService.get_link(db, short_code)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    LinkService.increment_clicks(db, short_code)

    return RedirectResponse(url=link.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(
    short_code: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    try:
        success = LinkService.delete_link(db, short_code, user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{short_code}", response_model=LinkResponse)
def update_link(
    short_code: str,
    link_update: LinkUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    try:
        link = LinkService.update_link(db, short_code, link_update, user_id)
        if not link:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
        return link
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{short_code}/stats", response_model=LinkStats)
def get_link_stats(
    short_code: str,
    db: Session = Depends(get_db)
):
    link = LinkService.get_link_stats(db, short_code)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    return link


@router.get("/search", response_model=List[LinkSearchResponse])
def search_by_original_url(
    original_url: str = Query(..., description="Original URL to search for"),
    db: Session = Depends(get_db)
):
    links = LinkService.search_by_original_url(db, original_url)
    return links


@router.post("/cleanup/expired", status_code=status.HTTP_200_OK)
def cleanup_expired_links(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authentication required")

    count = LinkService.cleanup_expired_links(db)
    return {"message": f"Deleted {count} expired links"}


@router.post("/cleanup/unused", status_code=status.HTTP_200_OK)
def cleanup_unused_links(
    days: int = Query(90, ge=1, le=365, description="Days of inactivity before cleanup"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authentication required")

    count = LinkService.cleanup_unused_links(db, days)
    return {"message": f"Deleted {count} unused links (inactive for {days}+ days)"}