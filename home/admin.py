from django.contrib import admin
from .models import Event, Order, Cart, CartItem, ChatRoom, Message

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


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ('sender', 'content', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = False


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('event', 'created_at', 'updated_at', 'message_count')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('event__title',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MessageInline]
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'chat_room', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('sender__username', 'content', 'chat_room__event__title')
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
