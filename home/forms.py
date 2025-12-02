from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'venue', 'latitude', 'longitude', 'ticket_price', 'ticket_availability', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event description',
                'rows': 5
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'venue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter venue location'
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'ticket_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ticket price',
                'step': '0.01',
                'min': '0'
            }),
            'ticket_availability': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter number of tickets available',
                'min': '0'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Event Title',
            'description': 'Event Description',
            'date': 'Event Date',
            'time': 'Event Time',
            'venue': 'Venue Location',
            'ticket_price': 'Ticket Price',
            'ticket_availability': 'Number of Tickets Available',
            'is_published': 'Publish Event'
        }

