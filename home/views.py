from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event
from .forms import EventForm

def index(request):
    template_data = {}
    template_data['title'] = 'Event Ticketer'
    events = Event.objects.filter(is_published=True)
    return render(request, 'home/index.html', {
        'template_data': template_data,
        'events': events
    })

def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request,
                  'home/about.html',
                  {'template_data': template_data})

@login_required
def create_event(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'event_organizer':
        messages.error(request, 'Only Event Organizers can create events.')
        return redirect('home.index')
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('home.event_detail', event_id=event.id)
    else:
        form = EventForm()
    
    template_data = {'title': 'Create Event'}
    return render(request, 'home/create_event.html', {
        'template_data': template_data,
        'form': form
    })

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    template_data = {'title': event.title}
    return render(request, 'home/event_detail.html', {
        'template_data': template_data,
        'event': event
    })

@login_required
def my_events(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'event_organizer':
        messages.error(request, 'Only Event Organizers can view this page.')
        return redirect('home.index')
    
    events = Event.objects.filter(organizer=request.user)
    template_data = {'title': 'My Events'}
    return render(request, 'home/my_events.html', {
        'template_data': template_data,
        'events': events
    })