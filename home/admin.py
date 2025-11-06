from django.contrib import admin
from .models import Event, Order

# Register your models here.

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'venue', 'ticket_price', 'ticket_availability', 'organizer', 'is_published', 'created_at')
    list_filter = ('is_published', 'date', 'created_at')
    search_fields = ('title', 'description', 'venue', 'organizer__username')
    date_hierarchy = 'date'
    ordering = ('-created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'attendee', 'event', 'quantity', 'unit_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('attendee__username', 'event__title')
    autocomplete_fields = ('attendee', 'event')
