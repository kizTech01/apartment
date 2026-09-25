from django.urls import path
from . import views
app_name = "bookings"
urlpatterns = [path("", views.booking_list, name="list"), path("request/<int:apartment_pk>/", views.request_booking, name="request"), path("<int:pk>/manage/", views.manage_booking, name="manage"), path("<int:pk>/cancel/", views.cancel_booking, name="cancel")]
