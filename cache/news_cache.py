from typing import List, Dict, Any, Optional

from config.cache_conf import get_json_cache, set_cache


CATEGORIES_KEY = "news:categories"


#获取新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)



async def set_cache_categories(data: List[Dict[str, Any]],expire: int = 7200):
    return await set_cache(CATEGORIES_KEY,data,expire)