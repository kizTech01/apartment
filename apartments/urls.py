from django.urls import path
from . import views
app_name = "apartments"
urlpatterns = [
    path("", views.home, name="home"), path("apartments/", views.apartment_list, name="list"),
    path("apartments/<int:pk>/", views.apartment_detail, name="detail"), path("apartments/mine/", views.my_apartments, name="my_apartments"),
    path("apartments/create/", views.apartment_create, name="create"), path("apartments/<int:pk>/edit/", views.apartment_edit, name="edit"),
    path("apartments/<int:pk>/images/add/", views.image_add, name="image_add"), path("apartments/<int:pk>/favourite/", views.toggle_favourite, name="toggle_favourite"), path("saved/", views.favourites, name="favourites"),
]
