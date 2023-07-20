from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models, oauth2, database

router = APIRouter(
    tags=['Admin'],
    prefix="/admin"
)


@router.post("/room", status_code=status.HTTP_201_CREATED)
async def create_room(new_room: schemas.RoomIN,
                      db: Session = Depends(database.get_db),
                      user_info: int = Depends(oauth2.get_current_user)):
    admin = db.query(models.Admins).filter(models.Admins.user_id == user_info.id).first()

    if not admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have access to create room!")

    room = db.query(models.Rooms).filter(models.Rooms.type == new_room.type,
                                         models.Rooms.name == new_room.name,
                                         models.Rooms.capacity == new_room.capacity).first()

    if room:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Room with such info already exist!")
    print(new_room)
    new_room = models.Rooms(**new_room.dict())
    db.add(new_room)
    db.commit()

    return {"message": "Room successfuly created!"}


@router.delete("/room", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(id: int,
                      db: Session = Depends(database.get_db),
                      user_info: schemas.UserOut = Depends(oauth2.get_current_user)):
    admin = db.query(models.Admins).filter(models.Admins.email == user_info.email).first()

    if not admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have access to create room!")

    room_query = db.query(models.Rooms) \
        .filter(models.Rooms.id == id)

    if not room_query.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Room with such info not exist!")

    room_query.delete()
    db.commit()

    return {"message": "Room successfuly deleted!"}
