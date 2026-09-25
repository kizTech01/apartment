from django.urls import path
from .views import report_listing
app_name = "moderation"
urlpatterns = [path("report/<int:apartment_pk>/", report_listing, name="report")]
