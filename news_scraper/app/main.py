# app/main.py
from typing import List, AsyncGenerator
from fastapi import FastAPI, Depends, HTTPException, status, Query, Path, Body
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncio
from fastapi.encoders import jsonable_encoder

from sqlalchemy.future import select
from . import models, crud, schemas
from .database import Base, engine, SessionLocal  
from .rss_scheduler import start_rss_feed_scheduler
from .config import get_logger
from fastapi.middleware.cors import CORSMiddleware
from .announce_models import Announcement
from .scraping_functions import scrape_incheon_announcements, scrape_gyeonggi_announcements, scraper_koroad_announcements
from .scraping_functions import scrape_bucheon_announcements, scrape_ulsan_announcements
from .scraper_seoul import scrape_seoul_announcements
from .scraper_gwangju import scrape_gwangju_announcements
from .scraper_incheon import scrape_incheon2_announcements
from .scraper_goyang import scrape_goyang_announcements
from .scraper_gangneung import scrape_gn_announcements
from .cache_management import load_cached_data, save_data_to_cache, get_md5_hash

logger = get_logger()

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Create database tables asynchronously
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Log that the application has started
    logger.info("Application started")

    # Start the RSS feed scheduler in the background
    task = asyncio.create_task(start_rss_feed_scheduler())

    yield

    # Attempt to cancel the task on cleanup
    task.cancel()

    # Log that the application has stopped
    logger.info("Application stopped")

app = FastAPI(lifespan=app_lifespan)

# Add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only, specify your frontend's domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection for AsyncSession
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

@app.post("/news", response_model=schemas.News, status_code=status.HTTP_201_CREATED)
def create_news_item(news: schemas.NewsCreate, db: AsyncSession = Depends(get_db)):
    return crud.create_news(db=db, news=news)

@app.get("/news", response_model=List[schemas.News])
async def read_news(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    news_items = await crud.get_news(db=db, skip=skip, limit=limit)  # Add 'await' here
    return news_items

@app.get("/news/{news_id}", response_model=schemas.News)
async def read_news_item(news_id: int, db: AsyncSession = Depends(get_db)):
    db_news = await crud.get_news_by_id(db=db, news_id=news_id)  # Correctly awaited
    if db_news is None:
        raise HTTPException(status_code=404, detail="News item not found")
    return db_news

@app.put("/news/{news_id}", response_model=schemas.News)
async def update_news_item(news_id: int, news: schemas.NewsCreate, db: AsyncSession = Depends(get_db)):
    updated_news = await crud.update_news(db=db, news_id=news_id, updated_news=news)  # Use await here
    if updated_news is None:
        raise HTTPException(status_code=404, detail="News item not found")
    return updated_news

@app.delete("/news/{news_id}", response_model=schemas.News)
def delete_news_item(news_id: int, db: AsyncSession = Depends(get_db)):
    deleted_news = crud.delete_news(db=db, news_id=news_id)
    if deleted_news is None:
        raise HTTPException(status_code=404, detail="News item not found")
    return deleted_news

@app.post("/news/{news_id}/vote", response_model=schemas.News)
async def vote_on_news(news_id: int, vote: schemas.VoteCreate, db: AsyncSession = Depends(get_db)):
    news_item = await crud.vote_news(db=db, news_id=news_id, vote_value=vote.vote_value)
    if not news_item:
        raise HTTPException(status_code=404, detail="News item not found")
    return news_item  # Directly return the ORM model, FastAPI will convert it based on your Pydantic schema

@app.get("/news/search/", response_model=List[schemas.News])
async def search_news(query: str = Query(...), db: AsyncSession = Depends(get_db)):
    news_query = select(models.News).where(models.News.title.contains(query)).limit(10)
    result = await db.execute(news_query)
    news_items = result.scalars().all()
    if not news_items:
        raise HTTPException(status_code=404, detail="No news found for your search")
    return news_items

# Community
@app.get("/community/", response_model=List[schemas.CommunityPost])
async def read_community_posts(db: AsyncSession = Depends(get_db)):
    posts = await crud.get_community_posts(db)
    return posts

@app.get("/community/{post_id}", response_model=schemas.CommunityPost)
async def read_community_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await crud.get_community_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.post("/community/", response_model=schemas.CommunityPost)
async def create_community_post(post: schemas.CommunityPostCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_community_post(db, post)

@app.put("/community/{post_id}", response_model=schemas.CommunityPost)
async def update_community_post(post_id: int, post: schemas.CommunityPostCreate, db: AsyncSession = Depends(get_db)):
    updated_post = await crud.update_community_post(db, post_id, post)
    if updated_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return updated_post

@app.delete("/community/{post_id}", response_model=schemas.CommunityPost)
async def delete_community_post(post_id: int, db: AsyncSession = Depends(get_db)):
    deleted_post = await crud.delete_community_post(db, post_id)
    if deleted_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return deleted_post

# 인천시 고시공고
@app.get("/announcements/incheon/", response_model=List[Announcement])
async def get_icn_announcements():
    try:
        announcements_data = scrape_incheon_announcements()
        return announcements_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching announcements: {str(e)}")
    
# 경기도 사업공고
@app.get("/announcements/gyeonggi/", response_model=List[Announcement])
async def get_gyeonggi_announcements():
    try:
        announcements_data = scrape_gyeonggi_announcements()
        return announcements_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching announcements: {str(e)}")

# 서울시 사업공고             
@app.get("/announcements/seoul/", response_model=List[Announcement])
async def get_seoul_announcements():
    try:
        # Ensure scrape_seoul_announcements() is awaited if it's an async function
        announcements_data = await scrape_seoul_announcements()
        return announcements_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching announcements: {str(e)}")
    
# 도로교통공단 사업공고
@app.get("/announcements/koroad/", response_model=List[Announcement])
async def get_koroad_announcements():
    try:
        announcements_data = scraper_koroad_announcements()
        return announcements_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching announcements: {str(e)}")
    
# 광주광역시 사업공고
@app.get("/announcements/gwangju/", response_model=List[Announcement])
async def get_gwangju_announcements():
    try:
        # Ensure scrape_seoul_announcements() is awaited if it's an async function
        announcements_data = await scrape_gwangju_announcements()
        return announcements_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching announcements: {str(e)}")
    
# 부천시 사업공고
@app.get("/announcements/bucheon/", response_model=List[Announcement])
async def get_bucheon_announcements():
    try:
        # Ensure scrape_seoul_announcements() is awaited if it's an async function
        announcements_data = scrape_bucheon_announcements()
        return announcements_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching announcements: {str(e)}")
    
# 울산광역시 사업공고
@app.get("/announcements/ulsan/", response_model=List[Announcement])
async def get_ulsan_announcements():
    try:
        # Ensure scrape_seoul_announcements() is awaited if it's an async function
        announcements_data = scrape_ulsan_announcements()
        return announcements_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching announcements: {str(e)}")
    
# 인천광역시 고시공고
@app.get("/announcements/incheon2/", response_model=List[Announcement])
async def get_incheon2_announcements():
    try:
        cached_data = await load_cached_data()
        new_data = await scrape_incheon2_announcements()
        if not cached_data or get_md5_hash(cached_data) != get_md5_hash(new_data):
            await save_data_to_cache(new_data)
        return new_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching announcements: {str(e)}")
    
# 고양시 고시공고
@app.get("/announcements/goyang/", response_model=List[Announcement])
async def get_goyang_announcements():
    try:
        cached_data = await load_cached_data()
        new_data = await scrape_goyang_announcements()
        if not cached_data or get_md5_hash(cached_data) != get_md5_hash(new_data):
            await save_data_to_cache(new_data)
        return new_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching announcements: {str(e)}")
    
# 강릉시 고시공고
@app.get("/announcements/gangneung/", response_model=List[Announcement])
async def get_gangneung_announcements():
    try:
        cached_data = await load_cached_data()
        new_data = await scrape_gn_announcements()
        if not cached_data or get_md5_hash(cached_data) != get_md5_hash(new_data):
            await save_data_to_cache(new_data)
        return new_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching announcements: {str(e)}")