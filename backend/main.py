
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://gk7380494:MNkeUCdbXJDStaAR@cluster0.6jrtbez.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.getenv("DB_NAME", "myapp")
SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gopal-1.onrender.com"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]


class UserIn(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr

class LoginIn(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_from_token(authorization: str = Header(None)):
   
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = parts[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_out = {"id": user["_id"], "name": user["name"], "email": user["email"]}
    return user_out


import uuid
def gen_id():
    return str(uuid.uuid4())

@app.post("/api/auth/signup", response_model=UserOut)
async def signup(payload: UserIn):
    existing = await users_collection.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_doc = {
        "_id": gen_id(),
        "name": payload.name,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "created_at": datetime.utcnow()
    }
    await users_collection.insert_one(user_doc)
    return {"id": user_doc["_id"], "name": user_doc["name"], "email": user_doc["email"]}

@app.post("/api/auth/login")
async def login(payload: LoginIn):
    user = await users_collection.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid Password or email")
    token = create_access_token({"sub": user["_id"]})
    return {"access_token": token, "token_type": "bearer", "user": {"id": user["_id"], "name": user["name"], "email": user["email"]}}

@app.get("/api/auth/me", response_model=UserOut)
async def me(current_user: dict = Depends(get_user_from_token)):

    return {"id": current_user["id"], "name": current_user["name"], "email": current_user["email"]}





app.mount("/", StaticFiles(directory="dist", html=True), name="dist")

# Sab unmatched routes React ke index.html pe bhejo
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    return FileResponse("dist/index.html")


