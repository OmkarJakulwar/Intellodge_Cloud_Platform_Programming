from django import forms

class RoomForm(forms.Form):
    room_number = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room Number'})
    )
    room_type = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room Type'})
    )
    price = forms.DecimalField(
        max_digits=8, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'})
    )
    status = forms.ChoiceField(
        choices=[('Vacant', 'Vacant'), ('Occupied', 'Occupied')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
