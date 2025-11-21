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
    path('orders/my-orders/', views.my_orders, name='home.my_orders'),
    # API endpoint for event search/filtering with JSON response
    path('events/api/', views.events_api, name='home.events_api'),
    # New events search page with filtering UI
    path('events/', views.events_search, name='home.events_search'),
    # Shopping cart URLs
    path('cart/', views.view_cart, name='home.view_cart'),
    path('cart/add/<int:event_id>/', views.add_to_cart, name='home.add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='home.remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='home.update_cart_quantity'),
]