from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from decimal import Decimal, InvalidOperation
from .models import Event
from .forms import EventForm

def index(request):
    """
    Display list of published events with optional filtering.
    Supports HTML rendering (default) and can handle query parameters for filtering.
    """
    template_data = {}
    template_data['title'] = 'Event Ticketer'
    
    # Get all published events
    events = Event.objects.filter(is_published=True)
    
    # Apply filters from query parameters (for backward compatibility and server-side filtering)
    name_filter = request.GET.get('name', '').strip()
    price_min = request.GET.get('price_min', '').strip()
    price_max = request.GET.get('price_max', '').strip()
    location_filter = request.GET.get('location', '').strip()
    
    # Filter by name (case-insensitive substring match)
    if name_filter:
        events = events.filter(title__icontains=name_filter)
    
    # Filter by price range
    if price_min:
        try:
            price_min_decimal = Decimal(price_min)
            events = events.filter(ticket_price__gte=price_min_decimal)
        except (InvalidOperation, ValueError):
            pass  # Invalid price_min value, ignore filter
    
    if price_max:
        try:
            price_max_decimal = Decimal(price_max)
            events = events.filter(ticket_price__lte=price_max_decimal)
        except (InvalidOperation, ValueError):
            pass  # Invalid price_max value, ignore filter
    
    # Filter by location (case-insensitive partial match)
    if location_filter:
        events = events.filter(venue__icontains=location_filter)
    
    # Order by creation date (newest first)
    events = events.order_by('-created_at')
    
    return render(request, 'home/index.html', {
        'template_data': template_data,
        'events': events,
        'current_filters': {
            'name': name_filter,
            'price_min': price_min,
            'price_max': price_max,
            'location': location_filter,
        }
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

@login_required
def edit_event(request, event_id):
    """
    Allow event organizers to edit their own events.
    This enables them to update event details and change draft status to published.
    """
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user is the organizer of this event
    if event.organizer != request.user:
        messages.error(request, 'You do not have permission to edit this event.')
        return redirect('home.event_detail', event_id=event.id)
    
    # Check if user is an event organizer
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'event_organizer':
        messages.error(request, 'Only Event Organizers can edit events.')
        return redirect('home.index')
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('home.event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
    
    template_data = {'title': f'Edit Event - {event.title}'}
    return render(request, 'home/edit_event.html', {
        'template_data': template_data,
        'form': form,
        'event': event
    })

def events_search(request):
    """
    Render the events search page with filtering UI.
    This page uses JavaScript to dynamically fetch and display filtered events from the API.
    """
    template_data = {'title': 'Search Events'}
    return render(request, 'home/events_search.html', {
        'template_data': template_data,
    })

def events_api(request):
    """
    API endpoint that returns paginated JSON responses for events with filtering support.
    Query parameters:
    - name: Filter by event name (case-insensitive substring)
    - price_min: Minimum ticket price
    - price_max: Maximum ticket price
    - location: Filter by venue location (case-insensitive partial match)
    - page: Page number for pagination (default: 1)
    - page_size: Number of items per page (default: 10, max: 100)
    """
    # Get all published events
    events = Event.objects.filter(is_published=True)
    
    # Extract and validate query parameters
    name_filter = request.GET.get('name', '').strip()
    price_min = request.GET.get('price_min', '').strip()
    price_max = request.GET.get('price_max', '').strip()
    location_filter = request.GET.get('location', '').strip()
    page_number = request.GET.get('page', '1')
    page_size = request.GET.get('page_size', '10')
    
    # Filter by name (case-insensitive substring match)
    if name_filter:
        events = events.filter(title__icontains=name_filter)
    
    # Filter by price range
    if price_min:
        try:
            price_min_decimal = Decimal(price_min)
            events = events.filter(ticket_price__gte=price_min_decimal)
        except (InvalidOperation, ValueError):
            return JsonResponse({
                'error': 'Invalid price_min value. Must be a valid decimal number.'
            }, status=400)
    
    if price_max:
        try:
            price_max_decimal = Decimal(price_max)
            events = events.filter(ticket_price__lte=price_max_decimal)
        except (InvalidOperation, ValueError):
            return JsonResponse({
                'error': 'Invalid price_max value. Must be a valid decimal number.'
            }, status=400)
    
    # Filter by location (case-insensitive partial match)
    if location_filter:
        events = events.filter(venue__icontains=location_filter)
    
    # Order by creation date (newest first)
    events = events.order_by('-created_at')
    
    # Pagination setup
    try:
        page_size = min(int(page_size), 100)  # Max 100 items per page
        page_size = max(page_size, 1)  # Min 1 item per page
    except (ValueError, TypeError):
        page_size = 10
    
    try:
        page_number = int(page_number)
        page_number = max(page_number, 1)
    except (ValueError, TypeError):
        page_number = 1
    
    paginator = Paginator(events, page_size)
    
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)
        page_number = 1
    
    # Serialize events to JSON
    events_data = []
    for event in page_obj:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'date': event.date.isoformat() if event.date else None,
            'time': event.time.strftime('%H:%M:%S') if event.time else None,
            'venue': event.venue,
            'ticket_price': str(event.ticket_price),
            'ticket_availability': event.ticket_availability,
            'organizer': {
                'id': event.organizer.id,
                'username': event.organizer.username,
                'full_name': event.organizer.get_full_name() or event.organizer.username,
            },
            'is_published': event.is_published,
            'created_at': event.created_at.isoformat() if event.created_at else None,
            'updated_at': event.updated_at.isoformat() if event.updated_at else None,
        })
    
    # Return paginated JSON response
    return JsonResponse({
        'count': paginator.count,
        'page': page_number,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'results': events_data,
    })