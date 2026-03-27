from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import users
from models.users import User
from schemas.users import UserAuthResponse, UserInfoResponse, UserRequest, UserUpdateRequest, UserChangePasswordRequest
from utils.auth import get_current_user
from utils.response import success_response

routers = APIRouter(prefix="/api/user", tags=["users"])


@routers.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    user = await users.get_user_by_username(db, username=user_data.username)
    if user:
        raise HTTPException(status_code=400, detail="用户已存在")

    user = await users.create_user(db, user_data)
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(
        token=token,
        user_info=UserInfoResponse.model_validate(user),
    )
    return success_response(message="注册成功", data=response_data)


@routers.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(
        token=token,
        user_info=UserInfoResponse.model_validate(user),
    )
    return success_response(message="登录成功", data=response_data)


@routers.get("/info")
async def get_user_info(current_user: User = Depends(get_current_user)):
    user_info = UserInfoResponse.model_validate(current_user)
    return success_response(
        message="获取用户信息成功",
        data={"userInfo": user_info},
    )


@routers.put("/update")
async def update_user_info(user_data: UserUpdateRequest, user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    user = await users.update_user(db, user.username, user_data)
    return success_response(message="更新用户信息成功", data=UserInfoResponse.model_validate(user))


@routers.put("/password")
async def update_password(
        password_data: UserChangePasswordRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    res_change_pwd = await users.change_password(db, user, password_data.old_password, password_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="修改密码失败，请稍后再试")
    return success_response(message="修改密码成功")