from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Booking, Customer, Room


class HotelViewTests(TestCase):
    def setUp(self):
        self.room = Room.objects.create(
            room_number="101",
            room_type="Single",
            price="100.00",
        )

    def test_home_displays_available_rooms(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Room 101")
        self.assertContains(response, reverse("book_room"))

    def test_booking_page_loads(self):
        response = self.client.get(reverse("book_room"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm Booking")

    def test_valid_booking_is_saved(self):
        check_in = timezone.localdate() + timezone.timedelta(days=1)
        check_out = check_in + timezone.timedelta(days=2)
        response = self.client.post(
            reverse("book_room"),
            {
                "full_name": "Alex Guest",
                "email": "alex@example.com",
                "phone": "123456789",
                "room": self.room.pk,
                "check_in": check_in.isoformat(),
                "check_out": check_out.isoformat(),
            },
        )

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(Customer.objects.count(), 1)

    def test_booking_rejects_overlapping_dates(self):
        check_in = timezone.localdate() + timezone.timedelta(days=1)
        check_out = check_in + timezone.timedelta(days=2)
        customer = Customer.objects.create(
            full_name="Existing Guest",
            email="existing@example.com",
            phone="987654321",
        )
        Booking.objects.create(
            customer=customer,
            room=self.room,
            check_in=check_in,
            check_out=check_out,
        )

        response = self.client.post(
            reverse("book_room"),
            {
                "full_name": "New Guest",
                "email": "new@example.com",
                "phone": "123456789",
                "room": self.room.pk,
                "check_in": check_in.isoformat(),
                "check_out": check_out.isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already booked")
        self.assertEqual(Booking.objects.count(), 1)
