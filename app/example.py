def get_available_times():
    # Set the working hours for the day
    start_time = datetime.strptime("09:00:00", "%H:%M:%S").time()
    end_time = datetime.strptime("21:00:00", "%H:%M:%S").time()

    available_times = []

    # Query booked times from the database
    session = SessionLocal()
    booked_times = session.query(Booking).filter(Booking.start >= datetime.now().date()).all()

    # Sort the booked times by start time
    booked_times.sort(key=lambda x: x.start)

    # Check the available time before the first booked time
    first_start = booked_times[0].start.time() if booked_times else end_time
    if start_time < first_start and datetime.combine(datetime.today(), first_start) - datetime.combine(datetime.today(), start_time) >= timedelta(minutes=15):
        available_times.append({"start": start_time, "end": first_start})

    # Check the available time between booked times
    for i in range(len(booked_times) - 1):
        current_end = booked_times[i].end.time()
        next_start = booked_times[i+1].start.time()

        if datetime.combine(datetime.today(), next_start) - datetime.combine(datetime.today(), current_end) >= timedelta(minutes=15):
            available_times.append({"start": current_end, "end": next_start})

    # Check the available time after the last booked time
    last_end = booked_times[-1].end.time() if booked_times else start_time
    if last_end < end_time and datetime.combine(datetime.today(), end_time) - datetime.combine(datetime.today(), last_end) >= timedelta(minutes=15):
        available_times.append({"start": last_end, "end": end_time})

    return available_times


def book_time_slot(booking_request: BookingRequest):
    # Convert request start and end times to datetime objects
    start_time = datetime.strptime(booking_request.start, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(booking_request.end, "%Y-%m-%d %H:%M:%S")

    # Validate the requested time slot
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="Invalid booking request. End time should be greater than start time.")

    # Query booked times from the database for validation
    session = SessionLocal()
    booked_times = session.query(Booking).filter(Booking.start >= datetime.now().date()).all()

    # Check for conflicts with existing bookings
    for booked_time in booked_times:
        if start_time < booked_time.end and end_time > booked_time.start:
            raise HTTPException(status_code=409, detail="Booking conflict. The requested time slot is not available.")

    # Create a new booking
    new_booking = Booking(start=start_time, end=end_time)
    session.add(new_booking)
    session.commit()

    return {"message": "Booking created successfully."}
