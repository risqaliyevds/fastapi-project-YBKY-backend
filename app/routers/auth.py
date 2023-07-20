from fastapi import APIRouter, Depends, status, HTTPException
from app import schemas, database, models, utils, oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter(
    tags=['AUTH'],
    prefix='/auth'
)


@router.post("/login", response_model=schemas.Token)
async def user_login(user_credentials: OAuth2PasswordRequestForm = Depends(),
                     db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Credentials")

    if not await utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Credentials")

    access_token = await oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
