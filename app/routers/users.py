from fastapi import APIRouter, Depends, status, HTTPException
from app import database, models, schemas, utils
from sqlalchemy.orm import Session

router = APIRouter(
    tags=['Users'],
    prefix="/users"
)


@router.post("/reg", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user_info: schemas.UserIn,
                      db: Session = Depends(database.get_db)):
    user = db.query(models.User) \
        .filter(models.User.email == user_info.email) \
        .first()

    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User with email -> {user_info.email} alredy exists")

    user_info.password = await utils.hashing(user_info.password)
    new_user = models.User(**user_info.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
