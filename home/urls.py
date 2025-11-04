from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home.index'),
    path('about', views.about, name='home.about'),
    path('events/create/', views.create_event, name='home.create_event'),
    path('events/<int:event_id>/', views.event_detail, name='home.event_detail'),
    path('events/my-events/', views.my_events, name='home.my_events'),
]