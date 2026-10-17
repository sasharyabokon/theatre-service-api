from django.contrib import admin

from theatre.models import Ticket, Performance, Play, Genre, Actor, TheatreHall

admin.site.register(Ticket)
admin.site.register(Performance)
admin.site.register(Play)
admin.site.register(Genre)
admin.site.register(Actor)
admin.site.register(TheatreHall)
