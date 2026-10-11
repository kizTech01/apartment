from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from accounts.models import LandlordVerification, User
from apartments.models import Apartment
from recommendations.services import recommend_apartments
from bookings.models import Booking
from messaging.models import Message
from moderation.models import ListingReport
from notifications.services import notify

from .forms import (
    ListingDecisionForm,
    ReportDecisionForm,
    UserAdministrationForm,
    VerificationDecisionForm,
)
from .permissions import administrator_required


def _admin_context():
    return {
        "kind": "admin",
        "stats": {
            "Total users": User.objects.count(),
            "Tenants": User.objects.filter(role=User.Role.TENANT).count(),
            "Verified owners": User.objects.filter(is_verified=True).count(),
            "Pending verifications": LandlordVerification.objects.filter(status=LandlordVerification.Status.PENDING).count(),
            "Pending listings": Apartment.objects.filter(status=Apartment.Status.PENDING).count(),
            "Open reports": ListingReport.objects.filter(status__in=[ListingReport.Status.PENDING, ListingReport.Status.REVIEWING]).count(),
        },
        "pending_verifications": LandlordVerification.objects.filter(status=LandlordVerification.Status.PENDING).select_related("user")[:5],
        "pending_listings": Apartment.objects.filter(status=Apartment.Status.PENDING).select_related("landlord")[:5],
        "pending_reports": ListingReport.objects.filter(status__in=[ListingReport.Status.PENDING, ListingReport.Status.REVIEWING]).select_related("apartment", "reporter")[:5],
    }

@login_required
def home(request):
    user = request.user
    if user.is_superuser or user.role == User.Role.ADMIN:
        context = _admin_context()
    elif user.is_property_owner:
        listings = user.apartments.all()
        context = {"kind": "owner", "stats": {"Total listings": listings.count(), "Live listings": listings.filter(status="AVAILABLE").count(), "Pending bookings": Booking.objects.filter(apartment__landlord=user, status="PENDING").count(), "Accepted bookings": Booking.objects.filter(apartment__landlord=user, status="ACCEPTED").count(), "Unread messages": Message.objects.filter(receiver=user, is_read=False).count()}, "listings": listings.prefetch_related("images")[:5]}
    else:
        context = {"kind": "tenant", "recommendations": recommend_apartments(user), "stats": {"Saved homes": user.favourites.count(), "Upcoming inspections": user.bookings.filter(status__in=["PENDING", "ACCEPTED", "RESCHEDULED"]).count(), "Unread messages": Message.objects.filter(receiver=user, is_read=False).count()}}
    return render(request, "dashboard/home.html", context)


@administrator_required
def verification_queue(request):
    status = request.GET.get("status", LandlordVerification.Status.PENDING)
    entries = LandlordVerification.objects.select_related("user", "reviewer")
    if status in LandlordVerification.Status.values:
        entries = entries.filter(status=status)
    return render(request, "dashboard/verification_queue.html", {"entries": entries, "selected_status": status, "statuses": LandlordVerification.Status.choices})


@administrator_required
def review_verification(request, pk):
    entry = get_object_or_404(LandlordVerification.objects.select_related("user", "reviewer"), pk=pk)
    form = VerificationDecisionForm(request.POST or None, initial={"decision": entry.status if entry.status != LandlordVerification.Status.PENDING else "APPROVED"})
    if request.method == "POST" and form.is_valid():
        entry.status = form.cleaned_data["decision"]
        entry.rejection_reason = form.cleaned_data["rejection_reason"].strip() if entry.status == LandlordVerification.Status.REJECTED else ""
        entry.reviewer = request.user
        entry.reviewed_at = timezone.now()
        entry.save(update_fields=("status", "rejection_reason", "reviewer", "reviewed_at"))
        owner = entry.user
        owner.is_verified = owner.verifications.filter(status=LandlordVerification.Status.APPROVED).exists()
        owner.save(update_fields=("is_verified",))
        outcome = "approved" if entry.status == LandlordVerification.Status.APPROVED else "rejected"
        notify(owner, "Account verification " + outcome, "Your verification submission has been " + outcome + ".", "VERIFICATION", "/accounts/verification/")
        messages.success(request, f"Verification {outcome}.")
        return redirect("dashboard:verification_queue")
    return render(request, "dashboard/review_verification.html", {"entry": entry, "form": form})


@administrator_required
def verification_document(request, pk):
    """Stream private verification evidence only to authorised administrators."""
    entry = get_object_or_404(LandlordVerification, pk=pk)
    if not entry.document:
        raise Http404("Verification document not found.")
    try:
        document = entry.document.open("rb")
    except FileNotFoundError as error:
        raise Http404("Verification document not found.") from error
    return FileResponse(document, as_attachment=True, filename=entry.document.name.rsplit("/", 1)[-1])


@administrator_required
def listing_queue(request):
    status = request.GET.get("status", Apartment.Status.PENDING)
    listings = Apartment.objects.select_related("landlord").prefetch_related("images")
    if status in Apartment.Status.values:
        listings = listings.filter(status=status)
    return render(request, "dashboard/listing_queue.html", {"listings": listings, "selected_status": status, "statuses": Apartment.Status.choices})


@administrator_required
def review_listing(request, pk):
    apartment = get_object_or_404(Apartment.objects.select_related("landlord").prefetch_related("images"), pk=pk)
    form = ListingDecisionForm(request.POST or None, initial={"decision": Apartment.Status.AVAILABLE, "moderation_note": apartment.moderation_note})
    if request.method == "POST" and form.is_valid():
        apartment.status = form.cleaned_data["decision"]
        apartment.moderation_note = form.cleaned_data["moderation_note"].strip()
        apartment.save(update_fields=("status", "moderation_note", "updated_at"))
        published = apartment.status == Apartment.Status.AVAILABLE
        notify(apartment.landlord, "Listing " + ("published" if published else "unpublished"), f'Your listing "{apartment.title}" has been {"published" if published else "unpublished"}.', "LISTING", "/apartments/mine/")
        messages.success(request, "Listing published." if published else "Listing unpublished.")
        return redirect("dashboard:listing_queue")
    return render(request, "dashboard/review_listing.html", {"apartment": apartment, "form": form})


@administrator_required
def report_queue(request):
    status = request.GET.get("status", ListingReport.Status.PENDING)
    reports = ListingReport.objects.select_related("apartment", "reporter", "apartment__landlord")
    if status in ListingReport.Status.values:
        reports = reports.filter(status=status)
    return render(request, "dashboard/report_queue.html", {"reports": reports, "selected_status": status, "statuses": ListingReport.Status.choices})


@administrator_required
def review_report(request, pk):
    report = get_object_or_404(ListingReport.objects.select_related("apartment", "reporter", "apartment__landlord"), pk=pk)
    form = ReportDecisionForm(request.POST or None, initial={"decision": "RESOLVED"})
    if request.method == "POST" and form.is_valid():
        report.status = form.cleaned_data["decision"]
        report.resolved_at = timezone.now()
        report.save(update_fields=("status", "resolved_at"))
        notify(report.reporter, "Listing report updated", f'Your report for "{report.apartment.title}" has been reviewed.', "REPORT", "/")
        messages.success(request, "Report updated.")
        return redirect("dashboard:report_queue")
    return render(request, "dashboard/review_report.html", {"report": report, "form": form})


@administrator_required
def user_list(request):
    query = request.GET.get("q", "").strip()
    users = User.objects.all().order_by("-created_at")
    if query:
        users = users.filter(Q(email__icontains=query) | Q(full_name__icontains=query) | Q(phone__icontains=query))
    return render(request, "dashboard/user_list.html", {"users": users, "query": query})


@administrator_required
def manage_user(request, pk):
    managed_user = get_object_or_404(User, pk=pk)
    if managed_user.is_superuser and not request.user.is_superuser:
        return redirect("dashboard:user_list")
    was_administrator = managed_user.role == User.Role.ADMIN
    form = UserAdministrationForm(request.POST or None, instance=managed_user)
    if request.method == "POST" and form.is_valid():
        if managed_user.pk == request.user.pk and (not form.cleaned_data["is_active"] or form.cleaned_data["role"] != User.Role.ADMIN):
            form.add_error(None, "You cannot deactivate your own account or remove your administrator role.")
        elif form.cleaned_data["role"] == User.Role.ADMIN and not request.user.is_superuser:
            form.add_error("role", "Only a superuser can grant administrator access.")
        elif was_administrator and not request.user.is_superuser:
            form.add_error("role", "Only a superuser can change another administrator account.")
        else:
            form.save()
            messages.success(request, "User account updated.")
            return redirect("dashboard:user_list")
    return render(request, "dashboard/manage_user.html", {"managed_user": managed_user, "form": form})
