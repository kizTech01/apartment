from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from apartments.models import Apartment
from .forms import ListingReportForm

@login_required
def report_listing(request, apartment_pk):
    if request.user.role != "TENANT": raise Http404
    apartment = get_object_or_404(Apartment, pk=apartment_pk)
    form = ListingReportForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        report = form.save(commit=False); report.apartment = apartment; report.reporter = request.user; report.save()
        messages.success(request, "Thank you. Your report has been sent for review."); return redirect("apartments:detail", pk=apartment.pk)
    return render(request, "moderation/report.html", {"form": form, "apartment": apartment})
