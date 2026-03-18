import secrets
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Tuple
from app.models import Link, User
from app.schemas import LinkCreate, LinkUpdate
from app.config import settings
from app.utils.redis_client import redis_client


class LinkService:
    SHORT_CODE_LENGTH = 6
    ALPHABET = string.ascii_letters + string.digits

    @staticmethod
    def generate_short_code() -> str:
        return ''.join(secrets.choice(LinkService.ALPHABET) for _ in range(LinkService.SHORT_CODE_LENGTH))

    @staticmethod
    def is_expired(expires_at: Optional[datetime]) -> bool:
        if expires_at is None:
            return False
        return datetime.utcnow() > expires_at

    @classmethod
    def create_link(
        cls,
        db: Session,
        link_data: LinkCreate,
        user_id: Optional[int] = None
    ) -> Tuple[Link, bool]:
        if link_data.custom_alias:
            existing = db.query(Link).filter(
                (Link.short_code == link_data.custom_alias) |
                (Link.custom_alias == link_data.custom_alias)
            ).first()
            if existing:
                raise ValueError(f"Custom alias '{link_data.custom_alias}' already exists")
            short_code = link_data.custom_alias
        else:
            short_code = cls.generate_short_code()
            while db.query(Link).filter(Link.short_code == short_code).first():
                short_code = cls.generate_short_code()

        link = Link(
            short_code=short_code,
            original_url=str(link_data.original_url),
            custom_alias=link_data.custom_alias,
            user_id=user_id,
            expires_at=link_data.expires_at
        )
        db.add(link)
        db.commit()
        db.refresh(link)

        cache_key = f"link:{short_code}"
        redis_client.set(cache_key, link, ttl=3600)

        return link, True

    @classmethod
    def get_link(cls, db: Session, short_code: str) -> Optional[Link]:
        cache_key = f"link:{short_code}"
        cached = redis_client.get(cache_key)
        if cached:
            if cls.is_expired(cached.expires_at):
                db.query(Link).filter(Link.short_code == short_code).delete()
                db.commit()
                redis_client.delete(cache_key)
                return None
            return cached

        link = db.query(Link).filter(Link.short_code == short_code).first()
        if link:
            if cls.is_expired(link.expires_at):
                db.query(Link).filter(Link.short_code == short_code).delete()
                db.commit()
                return None
            redis_client.set(cache_key, link, ttl=3600)
        return link

    @classmethod
    def update_link(
        cls,
        db: Session,
        short_code: str,
        link_update: LinkUpdate,
        user_id: Optional[int] = None
    ) -> Optional[Link]:
        link = db.query(Link).filter(Link.short_code == short_code).first()
        if not link:
            return None

        if link_update.original_url is not None:
            link.original_url = str(link_update.original_url)
        if link_update.custom_alias is not None:
            if link_update.custom_alias != link.custom_alias:
                existing = db.query(Link).filter(
                    (Link.short_code == link_update.custom_alias) |
                    (Link.custom_alias == link_update.custom_alias)
                ).first()
                if existing:
                    raise ValueError(f"Custom alias '{link_update.custom_alias}' already exists")
                link.custom_alias = link_update.custom_alias
                link.short_code = link_update.custom_alias
        if link_update.expires_at is not None:
            link.expires_at = link_update.expires_at

        db.commit()
        db.refresh(link)

        cache_key = f"link:{short_code}"
        redis_client.delete(cache_key)

        new_cache_key = f"link:{link.short_code}"
        redis_client.set(new_cache_key, link, ttl=3600)

        return link

    @classmethod
    def delete_link(cls, db: Session, short_code: str, user_id: Optional[int] = None) -> bool:
        link = db.query(Link).filter(Link.short_code == short_code).first()
        if not link:
            return False

        if user_id is not None and link.user_id != user_id:
            raise ValueError("Not authorized to delete this link")

        db.delete(link)
        db.commit()

        cache_key = f"link:{short_code}"
        redis_client.delete(cache_key)

        return True

    @classmethod
    def increment_clicks(cls, db: Session, short_code: str) -> Optional[Link]:
        link = db.query(Link).filter(Link.short_code == short_code).first()
        if link:
            link.clicks += 1
            link.last_clicked_at = datetime.utcnow()
            db.commit()
            db.refresh(link)

            cache_key = f"link:{short_code}"
            redis_client.set(cache_key, link, ttl=3600)

        return link

    @classmethod
    def get_link_stats(cls, db: Session, short_code: str) -> Optional[Link]:
        return cls.get_link(db, short_code)

    @classmethod
    def search_by_original_url(cls, db: Session, original_url: str) -> list[Link]:
        links = db.query(Link).filter(
            Link.original_url == original_url
        ).all()
        return links

    @classmethod
    def cleanup_expired_links(cls, db: Session) -> int:
        now = datetime.utcnow()
        expired = db.query(Link).filter(
            Link.expires_at.isnot(None),
            Link.expires_at < now
        ).all()

        count = 0
        for link in expired:
            cache_key = f"link:{link.short_code}"
            redis_client.delete(cache_key)
            db.delete(link)
            count += 1

        db.commit()
        return count

    @classmethod
    def cleanup_unused_links(cls, db: Session, days: int) -> int:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        unused = db.query(Link).filter(
            Link.last_clicked_at < cutoff_date,
            Link.clicks > 0
        ).all()

        count = 0
        for link in unused:
            cache_key = f"link:{link.short_code}"
            redis_client.delete(cache_key)
            db.delete(link)
            count += 1

        db.commit()
        return count