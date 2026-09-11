import datetime


def validate_seat_and_row(
    seat: int,
    row: int,
    max_seats_in_row: int,
    max_rows: int,
    exception: type[Exception],
):
    if not (1 <= seat <= max_seats_in_row):
        raise exception(
            f"Seat number {seat} doesn't exist in the plane. Please choose between 1 and {max_seats_in_row}"
        )
    elif not (1 <= row <= max_rows):
        raise exception(
            f"Row number {row} doesn't exist in the plane. Please choose between 1 and {max_rows}"
        )


def validate_source_destination(
    source: int, destination: int, exception: type[Exception]
):
    if source == destination:
        raise exception("Source and destination should be different")


def validate_date(
    departure_time: datetime.datetime,
    arrival_time: datetime.datetime,
    exception: type[Exception],
):
    if departure_time >= arrival_time:
        raise exception(
            "Departure time should be less than arrival time"
        )
