from django.db import transaction
from rest_framework import serializers

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

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance", "reservation")
        extra_kwargs = {
            "reservation": {"read_only": True}
        }

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        row = attrs.get("row")
        seat = attrs.get("seat")
        theatre_hall = attrs.get("performance").theatre_hall

        if not (1 <= row <= theatre_hall.rows):
            raise serializers.ValidationError(
                {"row": f"The row must be between 1 and {theatre_hall.rows}"}
            )
        if not (1 <= seat <= theatre_hall.seats_in_row):
            raise serializers.ValidationError(
                {"seat": f"The seat must be between 1 and {theatre_hall.seats_in_row}"}
            )
        return data


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
    tickets = TicketSerializer(read_only=False, many=True)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "user", "tickets")
        read_only_fields = ("id", "created_at", "user")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets", [])
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketSerializer(read_only=True, many=True)
