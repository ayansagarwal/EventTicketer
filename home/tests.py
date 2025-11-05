from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date, time
from .models import Event
from user_accounts.models import UserProfile


class EventSearchTests(TestCase):
    """Test cases for event search and filtering functionality."""
    
    def setUp(self):
        """
        Set up test data: create users and events for testing.
        """
        # Create test users
        self.user1 = User.objects.create_user(
            username='organizer1',
            email='org1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='organizer2',
            email='org2@test.com',
            password='testpass123'
        )
        
        # Update user profiles (created automatically by signal)
        self.user1.userprofile.user_type = 'event_organizer'
        self.user1.userprofile.save()
        self.user2.userprofile.user_type = 'event_organizer'
        self.user2.userprofile.save()
        
        # Create test events
        self.event1 = Event.objects.create(
            title='Jazz Concert',
            description='A wonderful jazz concert',
            date=date(2024, 12, 25),
            time=time(19, 0),
            venue='New York City, NY',
            ticket_price=Decimal('50.00'),
            ticket_availability=100,
            organizer=self.user1,
            is_published=True
        )
        
        self.event2 = Event.objects.create(
            title='Rock Music Festival',
            description='Amazing rock music festival',
            date=date(2024, 12, 30),
            time=time(18, 0),
            venue='Los Angeles, CA',
            ticket_price=Decimal('75.50'),
            ticket_availability=200,
            organizer=self.user2,
            is_published=True
        )
        
        self.event3 = Event.objects.create(
            title='Classical Music Night',
            description='Elegant classical music performance',
            date=date(2025, 1, 5),
            time=time(20, 0),
            venue='Chicago, IL',
            ticket_price=Decimal('30.00'),
            ticket_availability=50,
            organizer=self.user1,
            is_published=True
        )
        
        # Create an unpublished event (should not appear in search)
        self.event4 = Event.objects.create(
            title='Private Event',
            description='This should not appear',
            date=date(2025, 1, 10),
            time=time(15, 0),
            venue='Miami, FL',
            ticket_price=Decimal('100.00'),
            ticket_availability=10,
            organizer=self.user1,
            is_published=False
        )
        
        self.client = Client()
    
    def test_api_all_events(self):
        """Test API endpoint returns all published events when no filters applied."""
        url = reverse('home.events_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 3)  # Only published events
        self.assertEqual(len(data['results']), 3)
        self.assertIn('count', data)
        self.assertIn('page', data)
        self.assertIn('results', data)
    
    def test_api_filter_by_name_exact(self):
        """Test filtering events by exact name match."""
        url = reverse('home.events_api')
        response = self.client.get(url, {'name': 'Jazz Concert'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['title'], 'Jazz Concert')
    
    def test_api_filter_by_name_partial(self):
        """Test filtering events by partial name match (case-insensitive)."""
        url = reverse('home.events_api')
        response = self.client.get(url, {'name': 'music'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 2)
        titles = [event['title'] for event in data['results']]
        self.assertIn('Rock Music Festival', titles)
        self.assertIn('Classical Music Night', titles)
        self.assertNotIn('Jazz Concert', titles)
    
    def test_api_filter_by_name_case_insensitive(self):
        """Test that name filtering is case-insensitive."""
        url = reverse('home.events_api')
        response = self.client.get(url, {'name': 'JAZZ'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['title'], 'Jazz Concert')
    
    def test_api_filter_by_price_min(self):
        """Test filtering events by minimum price."""
        url = reverse('home.events_api')
        response = self.client.get(url, {'price_min': '50.00'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 2)
        for event in data['results']:
            self.assertGreaterEqual(Decimal(event['ticket_price']), Decimal('50.00'))
    
    def test_api_filter_by_price_max(self):
        """Test filtering events by maximum price."""
        url = reverse('home.events_api')
        response = self.client.get(url, {'price_max': '50.00'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 2)
        for event in data['results']:
            self.assertLessEqual(Decimal(event['ticket_price']), Decimal('50.00'))
    
    def test_api_filter_by_price_range(self):
        """Test filtering events by price range (min and max)."""
        url = reverse('home.events_api')
        response = self.client.get(url, {'price_min': '40.00', 'price_max': '60.00'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['title'], 'Jazz Concert')
    
    def test_api_filter_by_location_exact(self):
        """Test filtering events by exact location match."""
        url = reverse('home.events_api')
        response = self.client.get(url, {'location': 'New York City, NY'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['venue'], 'New York City, NY')
    
    def test_api_filter_by_location_partial(self):
        """Test filtering events by partial location match (case-insensitive)."""
        url = reverse('home.events_api')
        response = self.client.get(url, {'location': 'Angeles'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['venue'], 'Los Angeles, CA')
    
    def test_api_filter_by_location_case_insensitive(self):
        """Test that location filtering is case-insensitive."""
        url = reverse('home.events_api')
        response = self.client.get(url, {'location': 'CHICAGO'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['venue'], 'Chicago, IL')
    
    def test_api_filter_combined(self):
        """Test filtering events using multiple filters simultaneously."""
        url = reverse('home.events_api')
        response = self.client.get(url, {
            'name': 'Music',
            'price_min': '30.00',
            'price_max': '80.00',
            'location': 'Los Angeles'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['title'], 'Rock Music Festival')
    
    def test_api_pagination(self):
        """Test pagination in API response."""
        url = reverse('home.events_api')
        response = self.client.get(url, {'page_size': '2', 'page': '1'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['count'], 3)
        self.assertEqual(len(data['results']), 2)
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['page_size'], 2)
        self.assertEqual(data['total_pages'], 2)
        self.assertTrue(data['has_next'])
        self.assertFalse(data['has_previous'])
    
    def test_api_invalid_price_min(self):
        """Test API returns error for invalid price_min value."""
        url = reverse('home.events_api')
        response = self.client.get(url, {'price_min': 'invalid'})
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_api_invalid_price_max(self):
        """Test API returns error for invalid price_max value."""
        url = reverse('home.events_api')
        response = self.client.get(url, {'price_max': 'invalid'})
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_api_excludes_unpublished_events(self):
        """Test that API only returns published events."""
        url = reverse('home.events_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        titles = [event['title'] for event in data['results']]
        self.assertNotIn('Private Event', titles)
    
    def test_index_view_filter_by_name(self):
        """Test index view filtering by name."""
        url = reverse('home.index')
        response = self.client.get(url, {'name': 'Jazz'})
        
        self.assertEqual(response.status_code, 200)
        events = response.context['events']
        self.assertEqual(events.count(), 1)
        self.assertEqual(events.first().title, 'Jazz Concert')
    
    def test_index_view_filter_by_price_range(self):
        """Test index view filtering by price range."""
        url = reverse('home.index')
        response = self.client.get(url, {'price_min': '40.00', 'price_max': '60.00'})
        
        self.assertEqual(response.status_code, 200)
        events = response.context['events']
        self.assertEqual(events.count(), 1)
        self.assertEqual(events.first().title, 'Jazz Concert')
    
    def test_index_view_filter_by_location(self):
        """Test index view filtering by location."""
        url = reverse('home.index')
        response = self.client.get(url, {'location': 'Chicago'})
        
        self.assertEqual(response.status_code, 200)
        events = response.context['events']
        self.assertEqual(events.count(), 1)
        self.assertEqual(events.first().venue, 'Chicago, IL')
    
    def test_index_view_combined_filters(self):
        """Test index view with multiple filters."""
        url = reverse('home.index')
        response = self.client.get(url, {
            'name': 'Music',
            'price_min': '30.00',
            'price_max': '80.00'
        })
        
        self.assertEqual(response.status_code, 200)
        events = response.context['events']
        self.assertEqual(events.count(), 2)
    
    def test_index_view_preserves_filters_in_context(self):
        """Test that index view passes filter values to template context."""
        url = reverse('home.index')
        response = self.client.get(url, {
            'name': 'Test',
            'price_min': '10',
            'price_max': '20',
            'location': 'NYC'
        })
        
        self.assertEqual(response.status_code, 200)
        current_filters = response.context['current_filters']
        self.assertEqual(current_filters['name'], 'Test')
        self.assertEqual(current_filters['price_min'], '10')
        self.assertEqual(current_filters['price_max'], '20')
        self.assertEqual(current_filters['location'], 'NYC')
    
    def test_events_search_page_renders(self):
        """Test that the events search page renders successfully."""
        url = reverse('home.events_search')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search Events')
