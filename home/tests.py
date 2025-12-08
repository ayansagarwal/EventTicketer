from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date, time
from .models import Event, Order, ChatRoom, Message
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


class ChatTests(TestCase):
    """Test cases for chat functionality."""
    
    def setUp(self):
        """Set up test data for chat tests."""
        # Create organizer
        self.organizer = User.objects.create_user(
            username='organizer1',
            email='org1@test.com',
            password='testpass123'
        )
        self.organizer.userprofile.user_type = 'event_organizer'
        self.organizer.userprofile.save()
        
        # Create attendees
        self.attendee1 = User.objects.create_user(
            username='attendee1',
            email='att1@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.attendee1.userprofile.user_type = 'attendee'
        self.attendee1.userprofile.save()
        
        self.attendee2 = User.objects.create_user(
            username='attendee2',
            email='att2@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith'
        )
        self.attendee2.userprofile.user_type = 'attendee'
        self.attendee2.userprofile.save()
        
        # Create an attendee without orders
        self.attendee3 = User.objects.create_user(
            username='attendee3',
            email='att3@test.com',
            password='testpass123'
        )
        self.attendee3.userprofile.user_type = 'attendee'
        self.attendee3.userprofile.save()
        
        # Create event
        self.event = Event.objects.create(
            title='Test Concert',
            description='A test concert',
            date=date(2024, 12, 25),
            time=time(19, 0),
            venue='Test Venue',
            ticket_price=Decimal('50.00'),
            ticket_availability=100,
            organizer=self.organizer,
            is_published=True
        )
        
        # Create orders (paid tickets)
        self.order1 = Order.objects.create(
            attendee=self.attendee1,
            event=self.event,
            quantity=2,
            unit_price=Decimal('50.00'),
            status='paid'
        )
        
        self.order2 = Order.objects.create(
            attendee=self.attendee2,
            event=self.event,
            quantity=1,
            unit_price=Decimal('50.00'),
            status='paid'
        )
        
        self.client = Client()
    
    def test_chat_rooms_view_requires_login(self):
        """Test that chat rooms view requires login."""
        url = reverse('home.chat_rooms')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_chat_rooms_view_requires_attendee(self):
        """Test that only attendees can access chat rooms."""
        self.client.login(username='organizer1', password='testpass123')
        url = reverse('home.chat_rooms')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect with error
    
    def test_chat_rooms_view_shows_user_events(self):
        """Test that chat rooms view shows events where user has purchased tickets."""
        self.client.login(username='attendee1', password='testpass123')
        url = reverse('home.chat_rooms')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Concert')
        self.assertContains(response, 'My Chat Rooms')
    
    def test_chat_rooms_view_empty_when_no_orders(self):
        """Test that chat rooms view shows empty when user has no orders."""
        self.client.login(username='attendee3', password='testpass123')
        url = reverse('home.chat_rooms')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Chat Rooms Yet')
    
    def test_chat_room_detail_requires_login(self):
        """Test that chat room detail requires login."""
        url = reverse('home.chat_room_detail', args=[self.event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
    
    def test_chat_room_detail_requires_paid_order(self):
        """Test that user must have paid order to access chat room."""
        self.client.login(username='attendee3', password='testpass123')
        url = reverse('home.chat_room_detail', args=[self.event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect with error
    
    def test_chat_room_detail_accessible_with_order(self):
        """Test that user with paid order can access chat room."""
        self.client.login(username='attendee1', password='testpass123')
        url = reverse('home.chat_room_detail', args=[self.event.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Concert')
        self.assertContains(response, 'Chat')
    
    def test_chat_room_created_on_first_access(self):
        """Test that chat room is created when first accessed."""
        self.client.login(username='attendee1', password='testpass123')
        url = reverse('home.chat_room_detail', args=[self.event.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Chat room should be created
        self.assertTrue(ChatRoom.objects.filter(event=self.event).exists())
    
    def test_send_message_requires_login(self):
        """Test that sending message requires login."""
        url = reverse('home.send_message', args=[self.event.id])
        response = self.client.post(url, {'content': 'Test message'})
        self.assertEqual(response.status_code, 302)
    
    def test_send_message_requires_paid_order(self):
        """Test that user must have paid order to send message."""
        self.client.login(username='attendee3', password='testpass123')
        url = reverse('home.send_message', args=[self.event.id])
        response = self.client.post(url, {'content': 'Test message'})
        self.assertEqual(response.status_code, 302)
    
    def test_send_message_creates_message(self):
        """Test that sending message creates a Message object."""
        self.client.login(username='attendee1', password='testpass123')
        url = reverse('home.send_message', args=[self.event.id])
        response = self.client.post(url, {'content': 'Hello, everyone!'})
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Message.objects.filter(
            sender=self.attendee1,
            content='Hello, everyone!'
        ).exists())
    
    def test_send_message_empty_content_rejected(self):
        """Test that empty message content is rejected."""
        self.client.login(username='attendee1', password='testpass123')
        url = reverse('home.send_message', args=[self.event.id])
        response = self.client.post(url, {'content': ''})
        
        # Should redirect back with error
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Message.objects.filter(sender=self.attendee1).exists())
    
    def test_send_message_too_long_rejected(self):
        """Test that message exceeding max length is rejected."""
        self.client.login(username='attendee1', password='testpass123')
        url = reverse('home.send_message', args=[self.event.id])
        long_content = 'x' * 1001  # Exceeds 1000 character limit
        response = self.client.post(url, {'content': long_content})
        
        self.assertEqual(response.status_code, 302)
        # Message should not be created
        messages = Message.objects.filter(sender=self.attendee1)
        self.assertFalse(any(len(m.content) > 1000 for m in messages))
    
    def test_chat_messages_api_requires_login(self):
        """Test that chat messages API requires login."""
        url = reverse('home.chat_messages_api', args=[self.event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
    
    def test_chat_messages_api_requires_paid_order(self):
        """Test that chat messages API requires paid order."""
        self.client.login(username='attendee3', password='testpass123')
        url = reverse('home.chat_messages_api', args=[self.event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
    
    def test_chat_messages_api_returns_messages(self):
        """Test that chat messages API returns messages in JSON format."""
        # Create chat room and messages
        chat_room = ChatRoom.objects.create(event=self.event)
        message1 = Message.objects.create(
            chat_room=chat_room,
            sender=self.attendee1,
            content='First message'
        )
        message2 = Message.objects.create(
            chat_room=chat_room,
            sender=self.attendee2,
            content='Second message'
        )
        
        self.client.login(username='attendee1', password='testpass123')
        url = reverse('home.chat_messages_api', args=[self.event.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('messages', data)
        self.assertEqual(len(data['messages']), 2)
        self.assertEqual(data['messages'][0]['content'], 'First message')
        self.assertEqual(data['messages'][1]['content'], 'Second message')
    
    def test_chat_room_participants(self):
        """Test that chat room correctly identifies participants."""
        chat_room = ChatRoom.objects.create(event=self.event)
        participants = chat_room.get_participants()
        
        self.assertEqual(participants.count(), 2)
        self.assertIn(self.attendee1, participants)
        self.assertIn(self.attendee2, participants)
        self.assertNotIn(self.attendee3, participants)
    
    def test_chat_room_can_user_access(self):
        """Test chat room access control."""
        chat_room = ChatRoom.objects.create(event=self.event)
        
        # Attendee with paid order can access
        self.assertTrue(chat_room.can_user_access(self.attendee1))
        
        # Attendee without order cannot access
        self.assertFalse(chat_room.can_user_access(self.attendee3))
        
        # Organizer cannot access
        self.assertFalse(chat_room.can_user_access(self.organizer))
        
        # Anonymous user cannot access
        anonymous = User()
        self.assertFalse(chat_room.can_user_access(anonymous))
    
    def test_multiple_attendees_can_chat(self):
        """Test that multiple attendees can send messages in the same chat room."""
        chat_room = ChatRoom.objects.create(event=self.event)
        
        # Attendee1 sends message
        self.client.login(username='attendee1', password='testpass123')
        url = reverse('home.send_message', args=[self.event.id])
        self.client.post(url, {'content': 'Message from attendee1'})
        
        # Attendee2 sends message
        self.client.login(username='attendee2', password='testpass123')
        self.client.post(url, {'content': 'Message from attendee2'})
        
        # Both messages should exist
        self.assertEqual(Message.objects.filter(chat_room=chat_room).count(), 2)
        self.assertTrue(Message.objects.filter(sender=self.attendee1).exists())
        self.assertTrue(Message.objects.filter(sender=self.attendee2).exists())
    
    def test_chat_room_shows_participant_count(self):
        """Test that chat room shows correct participant count."""
        self.client.login(username='attendee1', password='testpass123')
        url = reverse('home.chat_room_detail', args=[self.event.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Should show 2 participants (attendee1 and attendee2)
        self.assertContains(response, '2 Participant')


class EventModerationTests(TestCase):
    """Test cases for event moderation functionality."""
    
    def setUp(self):
        """Set up test data for moderation tests."""
        # Create administrator
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        self.admin.userprofile.user_type = 'administrator'
        self.admin.userprofile.save()
        
        # Create organizer
        self.organizer = User.objects.create_user(
            username='organizer',
            email='org@test.com',
            password='testpass123'
        )
        self.organizer.userprofile.user_type = 'event_organizer'
        self.organizer.userprofile.save()
        
        # Create attendee
        self.attendee = User.objects.create_user(
            username='attendee',
            email='att@test.com',
            password='testpass123'
        )
        self.attendee.userprofile.user_type = 'attendee'
        self.attendee.userprofile.save()
        
        # Create pending event
        self.pending_event = Event.objects.create(
            title='Pending Event',
            description='This event is pending review',
            date=date(2024, 12, 25),
            time=time(19, 0),
            venue='Test Venue',
            ticket_price=Decimal('50.00'),
            ticket_availability=100,
            organizer=self.organizer,
            is_published=False,
            moderation_status='pending'
        )
        
        # Create approved event
        self.approved_event = Event.objects.create(
            title='Approved Event',
            description='This event is approved',
            date=date(2024, 12, 26),
            time=time(20, 0),
            venue='Test Venue 2',
            ticket_price=Decimal('75.00'),
            ticket_availability=50,
            organizer=self.organizer,
            is_published=True,
            moderation_status='approved'
        )
        
        # Create rejected event
        self.rejected_event = Event.objects.create(
            title='Rejected Event',
            description='This event was rejected',
            date=date(2024, 12, 27),
            time=time(21, 0),
            venue='Test Venue 3',
            ticket_price=Decimal('100.00'),
            ticket_availability=25,
            organizer=self.organizer,
            is_published=False,
            moderation_status='rejected',
            moderation_notes='Inappropriate content'
        )
        
        self.client = Client()
    
    def test_create_event_sets_pending_status(self):
        """Test that new events are created with pending status."""
        self.client.login(username='organizer', password='testpass123')
        url = reverse('home.create_event')
        
        response = self.client.post(url, {
            'title': 'New Test Event',
            'description': 'Test description',
            'date': '2024-12-30',
            'time': '18:00',
            'venue': 'Test Venue',
            'ticket_price': '50.00',
            'ticket_availability': '100',
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        event = Event.objects.get(title='New Test Event')
        self.assertEqual(event.moderation_status, 'pending')
        self.assertFalse(event.is_published)
    
    def test_pending_events_not_visible_to_public(self):
        """Test that pending events are not visible in public listings."""
        url = reverse('home.index')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        events = response.context['events']
        # Should only see approved events
        self.assertNotIn(self.pending_event, events)
        self.assertIn(self.approved_event, events)
        self.assertNotIn(self.rejected_event, events)
    
    def test_admin_moderation_requires_login(self):
        """Test that admin moderation page requires login."""
        url = reverse('home.admin_event_moderation')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_admin_moderation_requires_admin_role(self):
        """Test that only administrators can access moderation."""
        # Try as organizer
        self.client.login(username='organizer', password='testpass123')
        url = reverse('home.admin_event_moderation')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect with error
        
        # Try as attendee
        self.client.login(username='attendee', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect with error
    
    def test_admin_can_access_moderation(self):
        """Test that administrator can access moderation page."""
        # Refresh admin user to ensure userprofile is loaded
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.userprofile.user_type, 'administrator')
        
        self.client.login(username='admin', password='testpass123')
        url = reverse('home.admin_event_moderation')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Event Moderation')
        self.assertContains(response, self.pending_event.title)
    
    def test_admin_moderation_shows_pending_events(self):
        """Test that moderation page shows pending events."""
        self.client.login(username='admin', password='testpass123')
        url = reverse('home.admin_event_moderation')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        events = response.context['events']
        self.assertIn(self.pending_event, events)
        self.assertEqual(events.count(), 1)  # Only pending events by default
    
    def test_admin_moderation_filter_by_status(self):
        """Test filtering events by moderation status."""
        self.client.login(username='admin', password='testpass123')
        
        # Test approved filter
        url = reverse('home.admin_event_moderation') + '?status=approved'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        events = response.context['events']
        self.assertIn(self.approved_event, events)
        self.assertNotIn(self.pending_event, events)
        
        # Test rejected filter
        url = reverse('home.admin_event_moderation') + '?status=rejected'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        events = response.context['events']
        self.assertIn(self.rejected_event, events)
        self.assertNotIn(self.pending_event, events)
    
    def test_admin_event_review_page(self):
        """Test that admin can view event review page."""
        self.client.login(username='admin', password='testpass123')
        url = reverse('home.admin_event_review', args=[self.pending_event.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.pending_event.title)
        self.assertContains(response, 'Review Event')
    
    def test_approve_event_requires_admin(self):
        """Test that only admin can approve events."""
        # Try as organizer
        self.client.login(username='organizer', password='testpass123')
        url = reverse('home.admin_approve_event', args=[self.pending_event.id])
        response = self.client.post(url, {'notes': ''})
        self.assertEqual(response.status_code, 302)  # Redirect with error
    
    def test_approve_event_updates_status(self):
        """Test that approving an event updates its status."""
        self.client.login(username='admin', password='testpass123')
        url = reverse('home.admin_approve_event', args=[self.pending_event.id])
        response = self.client.post(url, {'notes': 'Looks good!'})
        
        self.assertEqual(response.status_code, 302)  # Redirect after approval
        self.pending_event.refresh_from_db()
        self.assertEqual(self.pending_event.moderation_status, 'approved')
        self.assertTrue(self.pending_event.is_published)
        self.assertEqual(self.pending_event.moderated_by, self.admin)
        self.assertIsNotNone(self.pending_event.moderated_at)
        self.assertEqual(self.pending_event.moderation_notes, 'Looks good!')
    
    def test_approve_event_makes_visible(self):
        """Test that approved events become visible to public."""
        self.client.login(username='admin', password='testpass123')
        url = reverse('home.admin_approve_event', args=[self.pending_event.id])
        self.client.post(url, {'notes': ''})
        
        # Check public listing
        self.client.logout()
        public_url = reverse('home.index')
        response = self.client.get(public_url)
        events = response.context['events']
        self.pending_event.refresh_from_db()
        self.assertIn(self.pending_event, events)
    
    def test_reject_event_requires_admin(self):
        """Test that only admin can reject events."""
        # Try as organizer
        self.client.login(username='organizer', password='testpass123')
        url = reverse('home.admin_reject_event', args=[self.pending_event.id])
        response = self.client.post(url, {'notes': 'Spam'})
        self.assertEqual(response.status_code, 302)  # Redirect with error
    
    def test_reject_event_requires_notes(self):
        """Test that rejecting an event requires notes."""
        self.client.login(username='admin', password='testpass123')
        url = reverse('home.admin_reject_event', args=[self.pending_event.id])
        response = self.client.post(url, {'notes': ''})
        
        # Should redirect back with error
        self.assertEqual(response.status_code, 302)
        self.pending_event.refresh_from_db()
        self.assertEqual(self.pending_event.moderation_status, 'pending')  # Still pending
    
    def test_reject_event_updates_status(self):
        """Test that rejecting an event updates its status."""
        self.client.login(username='admin', password='testpass123')
        url = reverse('home.admin_reject_event', args=[self.pending_event.id])
        response = self.client.post(url, {'notes': 'Inappropriate content'})
        
        self.assertEqual(response.status_code, 302)  # Redirect after rejection
        self.pending_event.refresh_from_db()
        self.assertEqual(self.pending_event.moderation_status, 'rejected')
        self.assertFalse(self.pending_event.is_published)
        self.assertEqual(self.pending_event.moderated_by, self.admin)
        self.assertIsNotNone(self.pending_event.moderated_at)
        self.assertEqual(self.pending_event.moderation_notes, 'Inappropriate content')
    
    def test_reject_event_keeps_hidden(self):
        """Test that rejected events remain hidden from public."""
        self.client.login(username='admin', password='testpass123')
        url = reverse('home.admin_reject_event', args=[self.pending_event.id])
        self.client.post(url, {'notes': 'Spam'})
        
        # Check public listing
        self.client.logout()
        public_url = reverse('home.index')
        response = self.client.get(public_url)
        events = response.context['events']
        self.pending_event.refresh_from_db()
        self.assertNotIn(self.pending_event, events)
    
    def test_event_approve_method(self):
        """Test Event.approve() method."""
        self.pending_event.approve(self.admin, 'Test approval notes')
        
        self.assertEqual(self.pending_event.moderation_status, 'approved')
        self.assertTrue(self.pending_event.is_published)
        self.assertEqual(self.pending_event.moderated_by, self.admin)
        self.assertIsNotNone(self.pending_event.moderated_at)
        self.assertEqual(self.pending_event.moderation_notes, 'Test approval notes')
    
    def test_event_reject_method(self):
        """Test Event.reject() method."""
        self.pending_event.reject(self.admin, 'Test rejection notes')
        
        self.assertEqual(self.pending_event.moderation_status, 'rejected')
        self.assertFalse(self.pending_event.is_published)
        self.assertEqual(self.pending_event.moderated_by, self.admin)
        self.assertIsNotNone(self.pending_event.moderated_at)
        self.assertEqual(self.pending_event.moderation_notes, 'Test rejection notes')
    
    def test_event_is_approved_property(self):
        """Test Event.is_approved property."""
        # Approved and published
        self.assertTrue(self.approved_event.is_approved)
        
        # Pending
        self.assertFalse(self.pending_event.is_approved)
        
        # Rejected
        self.assertFalse(self.rejected_event.is_approved)
        
        # Approved but not published
        self.approved_event.is_published = False
        self.approved_event.save()
        self.assertFalse(self.approved_event.is_approved)
    
    def test_moderation_statistics(self):
        """Test that moderation page shows correct statistics."""
        self.client.login(username='admin', password='testpass123')
        url = reverse('home.admin_event_moderation')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        stats = response.context['stats']
        self.assertEqual(stats['pending'], 1)
        self.assertEqual(stats['approved'], 1)
        self.assertEqual(stats['rejected'], 1)
        self.assertEqual(stats['total'], 3)
    
    def test_organizer_can_see_own_pending_events(self):
        """Test that organizer can see their own pending events in 'My Events'."""
        self.client.login(username='organizer', password='testpass123')
        url = reverse('home.my_events')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        events = response.context['events']
        # Organizer should see all their events regardless of status
        self.assertIn(self.pending_event, events)
        self.assertIn(self.approved_event, events)
        self.assertIn(self.rejected_event, events)
