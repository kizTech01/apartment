from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from apartments.models import Apartment, InteractionLog
from notifications.services import notify
from .forms import BookingForm, BookingResponseForm
from .models import Booking

@login_required
def request_booking(request, apartment_pk):
    if request.user.role != "TENANT": raise Http404
    apartment = get_object_or_404(Apartment, pk=apartment_pk, status=Apartment.Status.AVAILABLE)
    form = BookingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        booking = form.save(commit=False); booking.tenant = request.user; booking.apartment = apartment; booking.save()
        InteractionLog.objects.create(tenant=request.user, apartment=apartment, action=InteractionLog.Action.BOOKING)
        notify(apartment.landlord, "New inspection request", f"{request.user.full_name} requested an inspection for {apartment.title}.", "BOOKING", "/bookings/")
        messages.success(request, "Inspection request sent to the landlord."); return redirect("bookings:list")
    return render(request, "bookings/request.html", {"form": form, "apartment": apartment})

@login_required
def booking_list(request):
    if request.user.role == "TENANT": bookings = request.user.bookings.select_related("apartment", "apartment__landlord")
    elif request.user.is_property_owner: bookings = Booking.objects.filter(apartment__landlord=request.user).select_related("tenant", "apartment")
    else: bookings = Booking.objects.none()
    return render(request, "bookings/list.html", {"bookings": bookings})

@login_required
def manage_booking(request, pk):
    booking = get_object_or_404(Booking.objects.select_related("apartment", "tenant"), pk=pk, apartment__landlord=request.user)
    form = BookingResponseForm(request.POST or None, instance=booking)
    if request.method == "POST" and form.is_valid():
        form.save(); notify(booking.tenant, "Inspection request updated", f"Your inspection request for {booking.apartment.title} is now {booking.get_status_display().lower()}.", "BOOKING", "/bookings/")
        messages.success(request, "Booking updated."); return redirect("bookings:list")
    return render(request, "bookings/manage.html", {"form": form, "booking": booking})

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, tenant=request.user, status=Booking.Status.PENDING)
    if request.method == "POST":
        booking.status = Booking.Status.CANCELLED; booking.cancellation_reason = request.POST.get("reason", "Cancelled by tenant"); booking.save()
        notify(booking.apartment.landlord, "Inspection cancelled", f"{request.user.full_name} cancelled an inspection request for {booking.apartment.title}.", "BOOKING")
        messages.info(request, "Inspection request cancelled.")
    return redirect("bookings:list")
