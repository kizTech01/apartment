from django.urls import path
from . import views
app_name = "messaging"
urlpatterns = [path("", views.inbox, name="inbox"), path("start/<int:apartment_pk>/", views.start, name="start"), path("<int:apartment_pk>/<int:other_pk>/", views.thread, name="thread")]
