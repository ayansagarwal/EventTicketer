from django.contrib import admin
from .models import Event

# Register your models here.

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'venue', 'ticket_price', 'ticket_availability', 'organizer', 'is_published', 'created_at')
    list_filter = ('is_published', 'date', 'created_at')
    search_fields = ('title', 'description', 'venue', 'organizer__username')
    date_hierarchy = 'date'
    ordering = ('-created_at',)
