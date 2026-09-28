from django import forms
from intelroom.models.dynamo_rooms import Room
from datetime import date

class BookingForm(forms.Form):

    guest_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guest Name'}),
        label="Guest Name"
    )
    guest_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Guest Email'}),
        label="Guest Email"
    )
    room_number = forms.ChoiceField(
        label="Room Number",
        widget=forms.Select(attrs={"class": "form-select"}),
        required=False,  # optional if no rooms are available
    )

    amount = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Amount"}),
        label="Total Amount"
    )

    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Check-in Date"
    )

    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Check-out Date"
    )

    def __init__(self, *args, editing=False, **kwargs):
        super().__init__(*args, **kwargs)
        room_service = Room()
        # get all available rooms
        rooms = room_service.list_all()
        available_rooms = [
            (r["room_number"], f"{r['room_number']} - {r.get('room_type', 'Room')} (${r.get('price', 'N/A')})")
            for r in rooms if r.get("status") == "Vacant"
        ]

        if available_rooms:
            self.fields["room_number"].choices = available_rooms
        else:
            self.fields["room_number"].choices = [("", "No vacant rooms available")]
            self.fields["room_number"].disabled = True
            self.fields["room_number"].required = False
        
        if editing:
            self.fields['room_number'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get("check_in_date")
        check_out = cleaned_data.get("check_out_date")
        if check_in and check_out and check_out <= check_in:
            raise forms.ValidationError("Check-out must be after check-in.")
        if check_in and check_in < date.today():
            raise forms.ValidationError("Check-in cannot be in the past.")
        return cleaned_data
