from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ApartmentForm, ImageForm, SearchForm
from .models import Apartment, Favourite, InteractionLog

def home(request):
    featured = Apartment.objects.filter(status=Apartment.Status.AVAILABLE).select_related("landlord").prefetch_related("images")[:6]
    return render(request, "apartments/home.html", {"featured": featured, "form": SearchForm()})

def apartment_list(request):
    form = SearchForm(request.GET or None)
    listings = Apartment.objects.filter(status=Apartment.Status.AVAILABLE).select_related("landlord").prefetch_related("images")
    if form.is_valid():
        data = form.cleaned_data
        if data.get("location"): listings = listings.filter(location=data["location"])
        if data.get("min_price") is not None: listings = listings.filter(price__gte=data["min_price"])
        if data.get("max_price") is not None: listings = listings.filter(price__lte=data["max_price"])
        if data.get("bedrooms") is not None: listings = listings.filter(bedrooms__gte=data["bedrooms"])
        for amenity in data.get("amenities") or []: listings = listings.filter(amenities__contains=[amenity])
        listings = listings.order_by(data.get("sort") or "-created_at")
    return render(request, "apartments/list.html", {"form": form, "page_obj": Paginator(listings, 9).get_page(request.GET.get("page"))})

def apartment_detail(request, pk):
    apartment = get_object_or_404(Apartment.objects.select_related("landlord").prefetch_related("images"), pk=pk, status=Apartment.Status.AVAILABLE)
    if request.user.is_authenticated and request.user.role == "TENANT": InteractionLog.objects.create(tenant=request.user, apartment=apartment, action=InteractionLog.Action.VIEW)
    return render(request, "apartments/detail.html", {"apartment": apartment, "is_favourite": request.user.is_authenticated and Favourite.objects.filter(tenant=request.user, apartment=apartment).exists()})

@login_required
def my_apartments(request):
    if not request.user.is_property_owner: raise Http404
    return render(request, "apartments/my_apartments.html", {"apartments": request.user.apartments.prefetch_related("images").all()})

@login_required
def apartment_create(request):
    if not request.user.is_property_owner or not request.user.is_verified:
        messages.error(request, "Only administrator-verified landlords and agents may submit listings.")
        return redirect("accounts:verification")
    form = ApartmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        apartment = form.save(commit=False); apartment.landlord = request.user; apartment.status = Apartment.Status.PENDING; apartment.save()
        messages.success(request, "Listing submitted for administrator review. Add at least one photograph next.")
        return redirect("apartments:image_add", pk=apartment.pk)
    return render(request, "apartments/form.html", {"form": form, "heading": "List an apartment"})

@login_required
def apartment_edit(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk, landlord=request.user)
    form = ApartmentForm(request.POST or None, instance=apartment)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Listing updated."); return redirect("apartments:my_apartments")
    return render(request, "apartments/form.html", {"form": form, "heading": "Edit listing", "apartment": apartment})

@login_required
def image_add(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk, landlord=request.user)
    form = ImageForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        image = form.save(commit=False); image.apartment = apartment
        if image.is_primary: apartment.images.update(is_primary=False)
        image.save(); messages.success(request, "Photo uploaded."); return redirect("apartments:my_apartments")
    return render(request, "apartments/image_form.html", {"form": form, "apartment": apartment})

@login_required
def toggle_favourite(request, pk):
    if request.user.role != "TENANT": raise Http404
    apartment = get_object_or_404(Apartment, pk=pk, status=Apartment.Status.AVAILABLE)
    favourite, created = Favourite.objects.get_or_create(tenant=request.user, apartment=apartment)
    if created:
        InteractionLog.objects.create(tenant=request.user, apartment=apartment, action=InteractionLog.Action.SAVE); messages.success(request, "Saved to your favourites.")
    else: favourite.delete(); messages.info(request, "Removed from saved apartments.")
    return redirect(request.POST.get("next") or "apartments:detail", pk=pk)

@login_required
def favourites(request):
    if request.user.role != "TENANT": raise Http404
    return render(request, "apartments/favourites.html", {"favourites": Favourite.objects.filter(tenant=request.user).select_related("apartment", "apartment__landlord").prefetch_related("apartment__images")})
