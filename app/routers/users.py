import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

def get_password_hash(password: str) -> str:
    # Using SHA-256 for basic hashing as bcrypt/passlib is not in requirements
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Kiểm tra xem số điện thoại đã tồn tại trong hệ thống chưa
    db_user = db.query(models.user).filter(models.user.user_phone == user.user_phone).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số điện thoại này đã được đăng ký."
        )
    
    # Hash password và tạo record mới
    hashed_password = get_password_hash(user.password)
    
    new_user = models.user(**user.model_dump())
    
    # Lưu vào database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.get("/", response_model=list[schemas.UserResponse], status_code=status.HTTP_201_CREATED)
def get_users(db: Session = Depends(get_db)):
    return db.query(models.user).all()

@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.user).filter(models.user.user_id == user_id).first()

@router.put("/", response_model=schemas.UserResponse)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.user).filter(models.user.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = f"Không tìm thấy user với id: {user_id}")
    
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)

    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.user).filter(models.user.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = f"Không tìm thấy user với id: {user_id}")

    db.delete(user)
    db.commit()
    return None