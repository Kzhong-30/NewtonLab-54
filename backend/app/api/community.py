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

@router.post("/posts/", response_model=CommunityPostSchema, status_code=status.HTTP_201_CREATED)
def create_post(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    post_in: CommunityPostCreate
) -> Any:
    post = crud_community.create(db, obj_in=post_in, author_id=current_user.id)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "post_type": post.post_type,
        "author_id": post.author_id,
        "author_name": current_user.username,
        "created_at": post.created_at
    }


@router.put("/posts/{post_id}", response_model=CommunityPostSchema)
def update_post(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    post_id: int,
    post_in: CommunityPostUpdate
) -> Any:
    post = crud_community.get(db, id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )
    if post.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此帖子"
        )
    post = crud_community.update(db, db_obj=post, obj_in=post_in)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "post_type": post.post_type,
        "author_id": post.author_id,
        "author_name": post.author.username if post.author else None,
        "created_at": post.created_at
    }


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    post_id: int
) -> None:
    post = crud_community.get(db, id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )
    if post.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此帖子"
        )
    crud_community.remove(db, id=post_id)


@router.post("/posts/{post_id}/comments", response_model=CommentSchema, status_code=status.HTTP_201_CREATED)
def create_comment(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    post_id: int,
    comment_in: CommentCreate
) -> Any:
    post = crud_community.get(db, id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )
    comment = crud_community.add_comment(db, post_id=post_id, user_id=current_user.id, obj_in=comment_in)
    return {
        "id": comment.id,
        "content": comment.content,
        "post_id": comment.post_id,
        "author_id": comment.author_id,
        "author_name": current_user.username,
        "created_at": comment.created_at
    }


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    comment_id: int
) -> None:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    if comment.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此评论"
        )
    crud_community.delete_comment(db, comment_id=comment_id, user_id=current_user.id)
