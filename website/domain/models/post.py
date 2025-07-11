from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from website import db


class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        )
        # Add title field
    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        )
    overall_rating: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
        )

    story_rating: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
        )

    gameplay_rating: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
        )

    graphics_rating: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
        )

    sound_design_rating: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
        )

    replay_value_rating: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
        )

    difficulty_rating: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
        )

    bug_free_rating: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
        )

    pc_requirements_rating: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
        )

    game_length_blocks: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
        )

    game_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    game_developer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    author = relationship(
        "User",
        back_populates="posts",
        lazy="joined",
        passive_deletes=True,
    )
    images = relationship(
        "Image",
        secondary="post_images",
        back_populates="posts",
        lazy="subquery",
        order_by="Image.created_at",
    )
    saved_by = relationship(
        "SavedPost",
        back_populates="post",
        lazy="subquery",
        cascade="all, delete-orphan",
    )
    post_images = relationship(
        "PostImage",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="images"
    )
    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"Post:\n"
            f"ID: {self.id}\n"
            f"Title: {self.title!r}\n"
            f"Game Name: {self.game_name!r}\n"                # Added
            f"Game Developer: {self.game_developer!r}\n"      # Added
            f"Category: {self.category!r}\n" 
            f"Author ID: {self.author_id}\n"
            f"\nOverall Rating: {'★' * self.overall_rating + '☆' * (5 - self.overall_rating)}"
            f"\nStory: {'★' * self.story_rating + '☆' * (5 - self.story_rating)}"
            f"\nGameplay: {'★' * self.gameplay_rating + '☆' * (5 - self.gameplay_rating)}"
            f"\nGraphics: {'★' * self.graphics_rating + '☆' * (5 - self.graphics_rating)}"
            f"\nSound Design: {'★' * self.sound_design_rating + '☆' * (5 - self.sound_design_rating)}"
            f"\nReplay Value: {'★' * self.replay_value_rating + '☆' * (5 - self.replay_value_rating)}"
            f"\nDifficulty: {'★' * self.difficulty_rating + '☆' * (5 - self.difficulty_rating)}"
            f"\nBug Free? {'★' * self.bug_free_rating + '☆' * (5 - self.bug_free_rating)}"
            f"\nPC Requirements: {'★' * self.pc_requirements_rating + '☆' * (5 - self.pc_requirements_rating)}"
            f"\nGame Length: {'▰' * self.game_length_blocks + '▱' * (10 - self.game_length_blocks)}"
            f"Created At: {self.created_at}\n"
            f"Updated At: {self.updated_at}\n"
            f"Content: {self.content!r}"
        )


class SavedPost(db.Model):
    __tablename__ = "saved_posts"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="NO ACTION"),  # or omit ondelete entirely
        primary_key=True,
    )

    saved_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    user = relationship(
        "User",
        back_populates="saved_posts",
        passive_deletes=True,
    )
    post = relationship(
        "Post",
        back_populates="saved_by",
        passive_deletes=True,
        overlaps="post,post_images"
    )

    def __repr__(self) -> str:
        return (
            f"SavedPost:\n"
            f"User ID: {self.user_id}\n"
            f"Post ID: {self.post_id}\n"
            f"Saved At: {self.saved_at}"
        )


class PostImage(db.Model):
    __tablename__ = "post_images"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    image_id: Mapped[int] = mapped_column(
        ForeignKey("images.id", ondelete="NO ACTION"),
        primary_key=True,
    )

    post = relationship(
        "Post",
        back_populates="post_images",
        passive_deletes=True,
        overlaps="post,post_images,images"
    )
    image = relationship(
        "Image",
        back_populates="post_images",
        passive_deletes=True,
        overlaps="images"
    )

    def __repr__(self) -> str:
        return f"PostImage: post_id={self.post_id}, image_id={self.image_id}"


@event.listens_for(Post, "before_delete")
def _cleanup_comments(mapper, connection, target: Post):
    from .comment import Comment

    connection.execute(Comment.__table__.delete().where(Comment.post_id == target.id))
