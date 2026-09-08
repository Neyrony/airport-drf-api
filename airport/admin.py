from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from airport.models import (
    Airport,
    Route,
    Ticket,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
)

admin.site.unregister(Group)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "closest_big_city")
    ordering = ("name",)
    search_fields = ("name", "closest_big_city")
    fieldsets = ((None, {"fields": ("name", "closest_big_city")}),)
    list_per_page = 25


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
    ordering = ("source", "destination", "distance")
    search_fields = ("source__name", "destination__name")
    fieldsets = ((None, {"fields": ("source", "destination", "distance")}),)
    list_per_page = 25


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    ordering = ("name",)
    search_fields = ("name",)
    fieldsets = ((None, {"fields": ("name",)}),)
    list_per_page = 25


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("name", "rows", "seats_in_row", "airplane_type", "seats")
    ordering = ("name",)
    search_fields = ("name", "airplane_type__name")
    list_filter = ("rows", "seats_in_row")
    fieldsets = (
        (None, {"fields": ("name",)}),
        (_("Size"), {"fields": ("rows", "seats_in_row")}),
        (_("Type"), {"fields": ("airplane_type",)}),
    )
    list_per_page = 25


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")
    ordering = ("first_name", "last_name")
    search_fields = ("first_name", "last_name")
    fieldsets = ((None, {"fields": ("first_name", "last_name")}),)
    list_per_page = 25


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "route",
        "airplane",
        "departure_time",
        "arrival_time",
    )
    ordering = ("departure_time", "arrival_time")
    search_fields = ("route__source__name", "route__destination__name")
    fieldsets = (
        (None, {"fields": ("route", "airplane", "crews")}),
        ("Time", {"fields": ("departure_time", "arrival_time")}),
    )
    filter_horizontal = ("crews",)
    list_per_page = 25

    def get_queryset(self, request):
        return Flight.objects.select_related("route__destination", "route__source", "airplane")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "route":
            kwargs["queryset"] = Route.objects.select_related("source", "destination")

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TicketInLine(admin.TabularInline):
    model = Ticket
    extra = 1

    def formfield_for_foreignkey(
        self, db_field, request, **kwargs
    ):
        if db_field.name == "flight":
            kwargs["queryset"] = Flight.objects.select_related("airplane", "route__source", "route__destination")

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user")
    ordering = ("created_at",)
    search_fields = ("user__email",)
    fieldsets = ((None, {"fields": ("user", "created_at")}),)
    readonly_fields = ("created_at",)
    inlines = [
        TicketInLine,
    ]
    list_per_page = 25


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("row", "seat", "flight", "order")
    ordering = ("order",)
    search_fields = ("order__user__email", "flight__airplane__name")
    list_filter = ("row", "seat")
    fieldsets = (
        (None, {"fields": ("flight", "order")}),
        ("Seat", {"fields": ("seat", "row")}),
    )
    list_per_page = 25

    def get_queryset(self, request):
        return Ticket.objects.prefetch_related("flight__route__source", "flight__route__destination", "flight__airplane")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "flight":
            kwargs["queryset"] = Flight.objects.select_related("airplane", "route__source", "route__destination")
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
        