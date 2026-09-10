from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from airport.validators import validate_seat_and_row, validate_source_destination


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.closest_big_city})"

    class Meta:
        ordering = ["name"]


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination_routes"
    )
    distance = models.IntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )

    def clean(self):
        validate_source_destination(
            self.source.id, self.destination.id, ValidationError
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source.name} -> {self.destination.name}"

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["source", "destination"], name="unique_source_destination"
            )
        ]


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )
    seats_in_row = models.IntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.SET_NULL, related_name="airplanes", null=True
    )

    @property
    def seats(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crews = models.ManyToManyField(Crew, related_name="flights")

    def __str__(self):
        return f"{self.route} - {self.airplane}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )

    def __str__(self):
        return str(self.id)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    def __str__(self):
        return f"{self.row}-{self.seat}"

    def clean(self):
        validate_seat_and_row(
            self.seat,
            self.row,
            self.flight.airplane.seats_in_row,
            self.flight.airplane.rows,
            ValidationError,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["row", "seat", "flight"], name="unique_seat_flight"
            )
        ]
