from django.urls import path
from . import views
app_name = "dashboard"
urlpatterns = [
    path("", views.home, name="home"),
    path("administrator/verifications/", views.verification_queue, name="verification_queue"),
    path("administrator/verifications/<int:pk>/", views.review_verification, name="review_verification"),
    path("administrator/listings/", views.listing_queue, name="listing_queue"),
    path("administrator/listings/<int:pk>/", views.review_listing, name="review_listing"),
    path("administrator/reports/", views.report_queue, name="report_queue"),
    path("administrator/reports/<int:pk>/", views.review_report, name="review_report"),
    path("administrator/users/", views.user_list, name="user_list"),
    path("administrator/users/<int:pk>/", views.manage_user, name="manage_user"),
]
