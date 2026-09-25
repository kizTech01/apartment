from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from accounts.models import LandlordVerification, User
from apartments.models import Apartment
from recommendations.services import recommend_apartments
from bookings.models import Booking
from messaging.models import Message
from moderation.models import ListingReport

@login_required
def home(request):
    user = request.user
    if user.is_superuser or user.role == User.Role.ADMIN:
        context = {"kind": "admin", "stats": {"Total users": User.objects.count(), "Tenants": User.objects.filter(role=User.Role.TENANT).count(), "Verified owners": User.objects.filter(is_verified=True).count(), "Pending verifications": LandlordVerification.objects.filter(status="PENDING").count(), "Active listings": Apartment.objects.filter(status="AVAILABLE").count(), "Pending listings": Apartment.objects.filter(status="PENDING").count(), "Bookings": Booking.objects.count(), "Reported listings": ListingReport.objects.filter(status="PENDING").count()}, "pending_verifications": LandlordVerification.objects.filter(status="PENDING").select_related("user")[:5], "pending_listings": Apartment.objects.filter(status="PENDING").select_related("landlord")[:5]}
    elif user.is_property_owner:
        listings = user.apartments.all()
        context = {"kind": "owner", "stats": {"Total listings": listings.count(), "Live listings": listings.filter(status="AVAILABLE").count(), "Pending bookings": Booking.objects.filter(apartment__landlord=user, status="PENDING").count(), "Accepted bookings": Booking.objects.filter(apartment__landlord=user, status="ACCEPTED").count(), "Unread messages": Message.objects.filter(receiver=user, is_read=False).count()}, "listings": listings.prefetch_related("images")[:5]}
    else:
        context = {"kind": "tenant", "recommendations": recommend_apartments(user), "stats": {"Saved homes": user.favourites.count(), "Upcoming inspections": user.bookings.filter(status__in=["PENDING", "ACCEPTED", "RESCHEDULED"]).count(), "Unread messages": Message.objects.filter(receiver=user, is_read=False).count()}}
    return render(request, "dashboard/home.html", context)
