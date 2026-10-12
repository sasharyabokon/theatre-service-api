from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from theatre.models import (
    Actor,
    Genre,
    Play,
    TheatreHall,
    Performance,
    Reservation,
    Ticket
)


class ActorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name")


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ("id", "name")


class PlaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Play
        fields = ("id", "title", "description", "actors", "genres", "image")


class PlayImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "image")


class PlayListSerializer(PlaySerializer):
    genres = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )
    actors = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name",
    )


class PlayDetailSerializer(PlaySerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)


class TheatreHallSerializer(serializers.ModelSerializer):

    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seats_in_row")


class PerformanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time")


class PerformanceListSerializer(PerformanceSerializer):
    play = serializers.SlugRelatedField(
        read_only=True,
        slug_field="title",
    )
    play_image = serializers.ImageField(
        source="play.image",
        read_only=True
    )
    theatre_hall = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name",
    )

    class Meta(PerformanceSerializer.Meta):
        fields = ("id", "play", "play_image", "theatre_hall", "show_time")


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["performance"].theatre_hall,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance", "reservation")


class PerformanceDetailSerializer(PerformanceSerializer):
    play = PlayDetailSerializer(read_only=True)
    theatre_hall = TheatreHallSerializer(read_only=True)
    taken_places = TicketSerializer(
        source="tickets",
        many=True,
        read_only=True
    )

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time", "taken_places")


class ReservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "user", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            ticket_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket in ticket_data:
                Ticket.objects.create(reservation=reservation, **ticket)
            return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketSerializer(read_only=True, many=True)
