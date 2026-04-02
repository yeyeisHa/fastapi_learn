from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict




class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")


class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")


# 规划两个类： 一个是新闻模型类 + 收藏的模型类


# 收藏列表接口响应模型类
