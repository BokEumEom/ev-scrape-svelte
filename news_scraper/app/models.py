# app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import datetime
import pytz
from app.core.security import hash_password, verify_password

# Get the KST timezone
kst = pytz.timezone('Asia/Seoul')

def get_kst_now():
    return datetime.datetime.now(tz=kst)

class Region(Base):
    __tablename__ = "regions"
    name = Column(String, primary_key=True, index=True)

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    source = Column(String, nullable=False)
    link = Column(String, nullable=False)
    published_at = Column(DateTime, server_default=func.now())
    votes = relationship("Vote", back_populates="news")

class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey('news.id'))
    vote_value = Column(Integer, default=0)  # +1 for upvote, -1 for downvote
    news = relationship("News", back_populates="votes")
    
class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('community_posts.id'), nullable=False)


class CommunityPost(Base):
    __tablename__ = 'community_posts'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=get_kst_now)
    updated_at = Column(DateTime, default=get_kst_now, onupdate=get_kst_now)
    likeCount = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey('users.id'))  # 외래 키 추가

    # Relationships correctly defined once
    user = relationship("User")
    likes = relationship("CommunityPostLike", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan", order_by="Comment.created_at")
    
class CommunityPostLike(Base):
    __tablename__ = 'community_post_likes'
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('community_posts.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    post = relationship("CommunityPost", back_populates="likes")

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('community_posts.id'), nullable=False)
    content = Column(Text, nullable=False)  # Now Text is properly imported and recognized
    author = Column(String, nullable=True)  # Optional: Include if comments have visible authors
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    post = relationship("CommunityPost", back_populates="comments")
    
# Vehicle Spec
class VehicleSpec(Base):
    __tablename__ = 'vehicle_specs'
    
    id = Column(Integer, primary_key=True, index=True)
    manufacturer = Column(String, nullable=False)  # 제조사
    model = Column(String, nullable=False) # 모델명
    drive_type = Column(String)  # 드라이브 타입
    battery_type = Column(String)  # 배터리 타입
    battery_capacity = Column(Integer) # 배터리 용량
    range_km = Column(Integer)  # 주행 가능 거리
    acceleration = Column(Float)  # 도달 시간 (0-100 km/h)
    weight_kg = Column(Integer)  # 중량
    storage_l = Column(Integer)  # 적재공간
    wheel_size = Column(String)  # 휠 크기
    seating_capacity = Column(Integer)  # 좌석수
    display_inch = Column(Float)  # 디스플레이 크기
    minimum_ground_clearance_mm = Column(Integer)  # 최저 지상고
    width_mm = Column(Integer)  # 전폭
    height_mm = Column(Integer)  # 전고
    length_mm = Column(Integer)  # 전장
    created_at = Column(DateTime, default=func.now())  # 생성 일자
    
# Users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.hashed_password)

    def set_password(self, password: str):
        self.hashed_password = hash_password(password)
        
    # Relationship to CommunityPost
    posts = relationship("CommunityPost", back_populates="user")