from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserRole, PostType, CommunityPost, Comment
from ..schemas import CommunityPost as CommunityPostSchema, CommunityPostCreate, CommunityPostUpdate, Comment as CommentSchema, CommentCreate
from ..crud import community as crud_community
from ..core.security import get_current_user

router = APIRouter(prefix="/community", tags=["社区"])

@router.get("/posts/", response_model=List[CommunityPostSchema])
def get_posts(
    *,
    db: Session = Depends(get_db),
    post_type: Optional[PostType] = Query(None, description="帖子类型"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> Any:
    posts = crud_community.get_filtered(
        db,
        post_type=post_type,
        skip=skip,
        limit=limit
    )
    result = []
    for post in posts:
        result.append({"id": post.id, "title": post.title, "content": post.content, "post_type": post.post_type, "author_id": post.author_id, "author_name": post.author.username if post.author else None, "created_at": post.created_at})
    return result

@router.get("/posts/{post_id}", response_model=CommunityPostSchema)
def get_post(*, db: Session = Depends(get_db), post_id: int) -> Any:
    post = crud_community.get(db, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    return {"id": post.id, "title": post.title, "content": post.content, "post_type": post.post_type, "author_id": post.author_id, "author_name": post.author.username if post.author else None, "created_at": post.created_at}
