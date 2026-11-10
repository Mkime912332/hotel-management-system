from django import forms
from django.db import transaction
from django.utils import timezone

from .models import Booking, Customer, Room


class BookingForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    room = forms.ModelChoiceField(queryset=Room.objects.filter(is_available=True))
    check_in = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    check_out = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    def clean_check_in(self):
        check_in = self.cleaned_data["check_in"]
        if check_in < timezone.localdate():
            raise forms.ValidationError("Check-in date cannot be in the past.")
        return check_in

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")
        room = cleaned_data.get("room")

        if check_in and check_out and check_out <= check_in:
            self.add_error("check_out", "Check-out must be after check-in.")
        elif check_in and check_out and room:
            conflicting_booking = Booking.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in,
            ).exists()
            if conflicting_booking:
                self.add_error("room", "This room is already booked for those dates.")

        return cleaned_data

    @transaction.atomic
    def save(self):
        if not self.is_valid():
            raise ValueError("Cannot save an invalid booking form.")

        customer = Customer.objects.create(
            full_name=self.cleaned_data["full_name"],
            email=self.cleaned_data["email"],
            phone=self.cleaned_data["phone"],
        )
        return Booking.objects.create(
            customer=customer,
            room=self.cleaned_data["room"],
            check_in=self.cleaned_data["check_in"],
            check_out=self.cleaned_data["check_out"],
        )
