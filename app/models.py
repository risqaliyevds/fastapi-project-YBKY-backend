from app.database import Base
from sqlalchemy import Integer, String, TIMESTAMP, Column, ForeignKey, Date, func, text, Time, DateTime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    second_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)


class Rooms(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)


class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    # conf_date = Column(Date, nullable=False, default=func.current_date())
    booked_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))

class Admins(Base):
    __tablename__ = 'admins'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    email = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)