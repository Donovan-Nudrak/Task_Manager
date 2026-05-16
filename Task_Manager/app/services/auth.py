from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import TokenPayload, UserCreate

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode["exp"] = int(expire.timestamp())
    to_encode["iat"] = int(now.timestamp())
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token_payload(token: str) -> TokenPayload:
    payload_dict = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"require": ["exp", "sub"]},
    )
    return TokenPayload.model_validate(payload_dict)


def register_user(db: Session, user_data: UserCreate) -> User:
    if user_repository.get_user_by_email(db, user_data.email):
        raise ValueError("Email already registered")
    if user_repository.get_user_by_username(db, user_data.username):
        raise ValueError("Username already taken")
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = user_repository.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
