from django.contrib import admin
from .models import Event, Order, Cart, CartItem

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


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('event', 'quantity', 'added_at')
    readonly_fields = ('added_at',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_price', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'event', 'quantity', 'total_price', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('cart__user__username', 'event__title')
