from django.contrib import admin

from .models import Booking, Customer, Room


admin.site.register(Room)
admin.site.register(Customer)
admin.site.register(Booking)
