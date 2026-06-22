from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from .base import CRUDBase
from ..models import CommunityPost, Comment, CommunityLike, PostType
from ..schemas import CommunityPostCreate, CommunityPostUpdate, CommentCreate


class CRUDCommunity(CRUDBase[CommunityPost, CommunityPostCreate, CommunityPostUpdate]):
    def create(self, db: Session, *, obj_in: CommunityPostCreate, author_id: int) -> CommunityPost:
        obj_in_data = obj_in.model_dump(exclude={"rating", "is_spoiler"})
        db_obj = CommunityPost(**obj_in_data, author_id=author_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_type(self, db: Session, post_type: PostType, skip: int = 0, limit: int = 100) -> List[CommunityPost]:
        return db.query(CommunityPost).filter(
            CommunityPost.post_type == post_type,
            CommunityPost.is_approved == True
        ).offset(skip).limit(limit).all()

    def get_by_author(self, db: Session, author_id: int, skip: int = 0, limit: int = 100) -> List[CommunityPost]:
        return db.query(CommunityPost).filter(
            CommunityPost.author_id == author_id
        ).offset(skip).limit(limit).all()

    def get_filtered(
        self,
        db: Session,
        post_type: Optional[PostType] = None,
        author_id: Optional[int] = None,
        is_hot: Optional[bool] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CommunityPost]:
        query = db.query(CommunityPost).filter(CommunityPost.is_approved == True)
        if post_type:
            query = query.filter(CommunityPost.post_type == post_type)
        if author_id:
            query = query.filter(CommunityPost.author_id == author_id)
        if is_hot:
            query = query.filter(CommunityPost.is_hot == True)
        if keyword:
            query = query.filter(
                (CommunityPost.title.contains(keyword)) |
                (CommunityPost.content.contains(keyword))
            )
        return query.order_by(CommunityPost.created_at.desc()).offset(skip).limit(limit).all()

    def increment_view_count(self, db: Session, *, post_id: int) -> Optional[CommunityPost]:
        post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
        if not post:
            return None
        post.view_count += 1
        db.commit()
        db.refresh(post)
        return post

    def like_post(self, db: Session, *, post_id: int, user_id: int) -> Optional[CommunityPost]:
        post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
        if not post:
            return None
        existing_like = db.query(CommunityLike).filter(
            and_(CommunityLike.post_id == post_id, CommunityLike.user_id == user_id)
        ).first()
        if existing_like:
            db.delete(existing_like)
            post.like_count -= 1
        else:
            like = CommunityLike(post_id=post_id, user_id=user_id)
            db.add(like)
            post.like_count += 1
        db.commit()
        db.refresh(post)
        return post

    def get_post_stats(self, db: Session, post_id: int) -> Optional[dict]:
        post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
        if not post:
            return None
        comment_count = db.query(func.count(Comment.id)).filter(
            Comment.post_id == post_id,
            Comment.is_deleted == False
        ).scalar()
        return {
            "post_id": post.id,
            "view_count": post.view_count,
            "like_count": post.like_count,
            "comment_count": comment_count or 0
        }

    def add_comment(self, db: Session, *, post_id: int, user_id: int, obj_in: CommentCreate) -> Optional[Comment]:
        post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
        if not post:
            return None
        comment = Comment(
            **obj_in.model_dump(),
            post_id=post_id,
            author_id=user_id
        )
        db.add(comment)
        post.comment_count += 1
        db.commit()
        db.refresh(comment)
        return comment

    def get_comments(self, db: Session, post_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        return db.query(Comment).filter(
            Comment.post_id == post_id,
            Comment.is_deleted == False
        ).order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()

    def delete_comment(self, db: Session, *, comment_id: int, user_id: int) -> Optional[Comment]:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment or comment.author_id != user_id:
            return None
        comment.is_deleted = True
        post = db.query(CommunityPost).filter(CommunityPost.id == comment.post_id).first()
        if post and post.comment_count > 0:
            post.comment_count -= 1
        db.commit()
        db.refresh(comment)
        return comment


community = CRUDCommunity(CommunityPost)
