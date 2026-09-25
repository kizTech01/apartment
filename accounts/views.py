from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import LandlordRegistrationForm, PreferenceForm, RegistrationForm, VerificationForm
from .models import Preference, User


def register_tenant(request):
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False); user.role = User.Role.TENANT; user.save()
        login(request, user); messages.success(request, "Welcome to Smart Apartment. Tell us what home you are looking for.")
        return redirect("accounts:preferences")
    return render(request, "accounts/register.html", {"form": form, "account_type": "Tenant"})


def register_landlord(request):
    form = LandlordRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(); login(request, user)
        messages.info(request, "Upload a verification document before you create listings.")
        return redirect("accounts:verification")
    return render(request, "accounts/register.html", {"form": form, "account_type": "Landlord / Agent"})


@login_required
def verification(request):
    if not request.user.is_property_owner: return redirect("dashboard:home")
    form = VerificationForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False); entry.user = request.user; entry.save()
        messages.success(request, "Your document was submitted for review.")
        return redirect("accounts:verification")
    return render(request, "accounts/verification.html", {"form": form, "submissions": request.user.verifications.all()})


@login_required
def preferences(request):
    if request.user.role != User.Role.TENANT: return redirect("dashboard:home")
    preference, _ = Preference.objects.get_or_create(tenant=request.user)
    form = PreferenceForm(request.POST or None, instance=preference)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Your preferences are saved. Recommendations have been refreshed.")
        return redirect("dashboard:home")
    return render(request, "accounts/preferences.html", {"form": form})
