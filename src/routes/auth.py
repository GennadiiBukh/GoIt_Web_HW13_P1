from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas import UserCreate, UserResponse, Token, RefreshToken
from src.services.auth import create_access_token, verify_password, get_password_hash, secret_key, algorithm, \
    create_refresh_token, get_email_from_token

from src.services.email import send_email
from src.repository.users import get_user_by_email, register_user, confirm_email


router = APIRouter(prefix='/auth', tags=['auth'])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user_api(user: UserCreate, bt: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
    hashed_password = get_password_hash(user.password)
    new_user = register_user(db, user.username, user.email, hashed_password)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: RefreshToken, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token.refresh_token, secret_key, algorithms=[algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        # Перевірка, чи користувач існує в базі даних
        user = get_user_by_email(db, email)
        if not user:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Створення нового access токена
    access_token = create_access_token(data={"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = get_email_from_token(token)
    user = get_user_by_email(db, email)  # Перевірка, чи користувач існує в базі даних
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already confirmed")
    confirm_email(db, email)
    return {"message": "Email confirmed"}