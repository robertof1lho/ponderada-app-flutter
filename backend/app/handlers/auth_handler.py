import uuid
import aiomysql
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.db import get_pool
from app.core.security import hash_password, verify_password, create_token

router = APIRouter()


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register", status_code=201)
async def register(body: RegisterRequest):
    pool = await get_pool()
    user_id = str(uuid.uuid4())
    pw_hash = hash_password(body.password)
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO users (id, username, email, password_hash) VALUES (%s, %s, %s, %s)",
                    (user_id, body.username, body.email, pw_hash),
                )
    except Exception as e:
        raise HTTPException(status_code=409, detail="Username or email already exists")
    return {"id": user_id, "token": create_token(user_id)}


@router.post("/login")
async def login(body: LoginRequest):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT id, password_hash FROM users WHERE email = %s",
                (body.email,),
            )
            user = await cur.fetchone()
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"id": user["id"], "token": create_token(user["id"])}
