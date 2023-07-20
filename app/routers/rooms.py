from fastapi import APIRouter, Depends, status, HTTPException
from app import schemas, database, models, oauth2
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date
from app.config import settings

router = APIRouter(
    tags=['Rooms'],
    prefix='/rooms'
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=schemas.Rooms)
async def exist_rooms(search: Optional[str] = "",
                      room_type: Optional[str] = "",
                      db: Session = Depends(database.get_db)):
    query = db.query(models.Rooms) \
        .filter(models.Rooms.name.contains(search)) \
        .filter(models.Rooms.type.contains(room_type))
    serialized_results = []
    for room in query.all():
        serialized_room = schemas.RoomOUT(**room.__dict__)
        serialized_results.append(serialized_room)

    return {"count": len(serialized_results), "results": serialized_results}


async def is_room_not_exist(id: int,
                            db: Session = Depends(database.get_db)):
    room = db.query(models.Rooms).filter(models.Rooms.id == id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with id -> {id} not found")


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.RoomOUT)
async def find_room_by_id(id: int,
                          db: Session = Depends(database.get_db)):
    await is_room_not_exist(id, db)
    room = db.query(models.Rooms).filter(models.Rooms.id == id).first()
    return room


@router.get("/{id}/availability",
            status_code=status.HTTP_200_OK,
            response_model=List[schemas.RoomAvailability])
async def room_availability(
        id: int,
        date: Optional[date] = date.today(),
        db: Session = Depends(database.get_db)):
    await is_room_not_exist(id, db)

    OPEN_TIME = datetime.strptime(settings.OPEN_TIME, "%H:%M:%S").time()
    CLOSE_TIME = datetime.strptime(settings.CLOSE_TIME, "%H:%M:%S").time()

    if date == datetime.now().date():
        OPEN_TIME = datetime.now().time()

    booked_times = db.query(models.Booking).filter(
        models.Booking.start_time >= datetime.combine(date, OPEN_TIME),
        models.Booking.end_time <= datetime.combine(date, CLOSE_TIME),
    ).all()

    booked_times.sort(key=lambda x: x.start_time)

    available_periods = []

    current_time = datetime.combine(date, OPEN_TIME)
    end_time = datetime.combine(date, CLOSE_TIME)

    if not booked_times:
        available_periods.append({
            "start": current_time,
            "end": end_time
        })
        return available_periods

    first_booking_start = min(booking.start_time for booking in booked_times)
    if OPEN_TIME < first_booking_start.time():
        available_periods.append({
            "start": current_time.strftime("%Y-%m-%d %H:%M:00"),
            "end": first_booking_start.strftime("%Y-%m-%d %H:%M:00")
        })

    for i in range(len(booked_times) - 1):
        current_booking_end = booked_times[i].end_time
        next_booking_start = booked_times[i + 1].start_time
        if current_booking_end.time() < next_booking_start.time():
            available_periods.append({
                "start": current_booking_end.strftime("%Y-%m-%d %H:%M:00"),
                "end": next_booking_start.strftime("%Y-%m-%d %H:%M:00")
            })

    last_booking_end = max(booking.end_time for booking in booked_times)
    if last_booking_end.time() < CLOSE_TIME:
        available_periods.append({
            "start": last_booking_end.strftime("%Y-%m-%d %H:%M:00"),
            "end": end_time.strftime("%Y-%m-%d %H:%M:00")
        })

    return available_periods


@router.post("/{id}/book")
async def book_room(id: int,
                    booking_request: schemas.RoomAvailability,
                    db: Session = Depends(database.get_db),
                    user_info: schemas.UserID = Depends(oauth2.get_current_user)):
    await is_room_not_exist(id, db)

    start_time = booking_request.start
    end_time = booking_request.end

    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:00")
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:00")

    if start_time.time() >= end_time.time():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid booking request. End time should be greater then start time!")

    if start_time < datetime.now():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid booking request. Booking hours or date not correct!")

    if start_time.date() != end_time.date():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid booking request. Booking should planned for one day!")

    OPEN_TIME = datetime.strptime(settings.OPEN_TIME, "%H:%M:%S").time()
    CLOSE_TIME = datetime.strptime(settings.CLOSE_TIME, "%H:%M:%S").time()

    if start_time.time() < OPEN_TIME or end_time.time() > CLOSE_TIME:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid booking request. Booking out of working hours!")

    booked_times = db.query(models.Booking).filter(
        models.Booking.start_time >= datetime.combine(booking_request.start.date(), OPEN_TIME),
        models.Booking.end_time <= datetime.combine(booking_request.end.date(), CLOSE_TIME),
    ).all()

    booked_times.sort(key=lambda x: x.start_time)

    for booked_time in booked_times:
        if start_time < booked_time.end_time and end_time > booked_time.start_time:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Booking conflict. The requested time slot is not available.")

    new_booking = models.Booking(start_time=start_time,
                                 end_time=end_time,
                                 room_id=id,
                                 user_id=user_info.id)

    db.add(new_booking)
    db.commit()

    user = db.query(models.User).filter(models.User.id == user_info.id).first()
    return {"resident": {"name": f"{user.first_name} {user.second_name}"},
            "start": start_time_str,
            "end": end_time_str}


@router.get("/{id}/my bookings",
            status_code=status.HTTP_200_OK)
async def room_availability(
        user_info: schemas.UserID = Depends(oauth2.get_current_user),
        db: Session = Depends(database.get_db)):
    booked_list = db.query(models.Booking).filter(
        models.Booking.user_id == user_info.id).all()

    booked_list.sort(key=lambda x: x.start_time)

    available_bookings = []

    if not booked_list:
        return {"message": "You don't have any booked hours!"}

    for booked_hour in booked_list:
        serialized_hours = {"booked_id": booked_hour.id,
                            "start": booked_hour.start_time,
                            "end": booked_hour.end_time}
        room = db.query(models.Rooms).filter(models.Rooms.id == int(booked_hour.room_id)).first()
        available_bookings.append({"room": room, "hours": serialized_hours})

    return available_bookings


@router.delete("/id", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(id: int,
                         user_info: schemas.UserID = Depends(oauth2.get_current_user),
                         db: Session = Depends(database.get_db)):
    booked_time_query = db.query(models.Booking) \
        .filter(models.Booking.id == id, models.Booking.user_id == user_info.id)

    if not booked_time_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Booked hours with id -> {id} not found!")

    booked_time_query.delete()
    db.commit()
    #return {"message": "Booked time successfuly deleted!"}
