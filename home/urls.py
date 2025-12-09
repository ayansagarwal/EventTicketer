from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home.index'),
    path('about', views.about, name='home.about'),
    path('events/create/', views.create_event, name='home.create_event'),
    path('events/<int:event_id>/', views.event_detail, name='home.event_detail'),
    path('events/<int:event_id>/edit/', views.edit_event, name='home.edit_event'),
    path('events/<int:event_id>/buy/', views.buy_ticket, name='home.buy_ticket'),
    path('events/my-events/', views.my_events, name='home.my_events'),
    path('dashboard/', views.dashboard, name='home.dashboard'),
    path('orders/my-orders/', views.my_orders, name='home.my_orders'),
    # API endpoint for event search/filtering with JSON response
    path('events/api/', views.events_api, name='home.events_api'),
    # New events search page with filtering UI
    path('events/', views.events_search, name='home.events_search'),
    # Interactive map view for attendees
    path('events/map/', views.events_map, name='home.events_map'),
    # Shopping cart URLs
    path('cart/', views.view_cart, name='home.view_cart'),
    path('cart/add/<int:event_id>/', views.add_to_cart, name='home.add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='home.remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='home.update_cart_quantity'),
    # Chat URLs
    path('chat/', views.chat_rooms, name='home.chat_rooms'),
    path('chat/<int:event_id>/', views.chat_room_detail, name='home.chat_room_detail'),
    path('chat/<int:event_id>/send/', views.send_message, name='home.send_message'),
    path('chat/<int:event_id>/api/', views.chat_messages_api, name='home.chat_messages_api'),
    # Admin/Moderation URLs
    path('admin/moderation/', views.admin_event_moderation, name='home.admin_event_moderation'),
    path('admin/moderation/<int:event_id>/', views.admin_event_review, name='home.admin_event_review'),
    path('admin/moderation/<int:event_id>/approve/', views.admin_approve_event, name='home.admin_approve_event'),
    path('admin/moderation/<int:event_id>/reject/', views.admin_reject_event, name='home.admin_reject_event'),
    # Admin User Management URLs
    path('admin/users/', views.admin_user_management, name='home.admin_user_management'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='home.admin_user_detail'),
    path('admin/users/<int:user_id>/edit-role/', views.admin_user_edit_role, name='home.admin_user_edit_role'),
]