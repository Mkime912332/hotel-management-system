from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import BookingForm
from .models import Room


def home(request):
    rooms = Room.objects.filter(is_available=True).order_by("room_number")
    return render(request, "home.html", {"rooms": rooms})


def book_room(request):
    initial = {}
    if request.method == "GET" and request.GET.get("room"):
        initial["room"] = request.GET["room"]

    form = BookingForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your room has been booked successfully.")
        return redirect("home")

    return render(request, "book_room.html", {"form": form})
