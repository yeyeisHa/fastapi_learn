from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import Category, News
from cache.news_cache import get_cached_categories, set_cache_categories, get_cache_news_list, set_cache_news_list, \
    get_cached_news_detail, cache_news_detail, get_cached_related_news, cache_related_news
from models.news import Category, News
from schemas.base import NewsItemBase
from schemas.news import NewsDetailResponse, RelatedNewsResponse
async def get_categories(db:AsyncSession,skip:int = 0,limit:int = 100):
    cache_categories = await get_cached_categories()
    if cache_categories:
        return cache_categories
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)

    cache_categories = result.scalars().all()
    if cache_categories:
        cache_categories = jsonable_encoder(cache_categories)
        await set_cache_categories(cache_categories)
    return cache_categories


# 获取新闻列表
async def get_news_list(db:AsyncSession,category_id:int, skip:int = 0,limit:int = 100):
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


# 获取新闻数量
async def get_news_count(db:AsyncSession,category_id:int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()


# 获取新闻详情
async def get_news_detail(db:AsyncSession,news_id:int):

    cached_news = await get_cached_news_detail(news_id)
    if cached_news:
        return News(**cached_news)

    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news = result.scalar_one_or_none()

    if news:
        new_dict = NewsDetailResponse.model_validate(news).model_dump(
            by_alias=False,mode="json",exclude={"related_news"}
        )
        await cache_news_detail(news_id,new_dict)
    return  news


# 更新新闻浏览量
async def increase_news_views(db:AsyncSession,news_id:int):
    stmt = update(News).where(News.id == news_id).values(views=News.views+1)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


# 获取相关新闻列表
async def get_related_news(db:AsyncSession,news_id:int,category_id:int,limit:int = 5):

    cache_related = await get_cached_related_news(news_id,category_id)
    if cache_related:
        return cache_related

    stmt = (select(News).where(News.category_id == category_id).where(News.id != news_id).
            order_by(News.views.desc(),
                     News.publish_time.desc())
            .limit(limit))
    result = await db.execute(stmt)
    related_news =  result.scalars().all()

    if related_news:
        related_data = [
            RelatedNewsResponse.model_validate(news).model_dump(by_alias=False,mode="json")
            for news in related_news
        ]
        await cache_related_news(news_id,category_id,related_data)
        return related_data
    return []

