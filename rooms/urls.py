from django.urls import path
from . import views

# for Django Templates
# urlpatterns = [
#     path("", views.see_all_rooms),
#     path("<int:room_pk>", views.see_one_room),
# ]

urlpatterns = [
    path("", views.Rooms.as_view()),
    path("<int:pk>", views.RoomDetail.as_view()),
    path("amenities/", views.Amenities.as_view()),
    path("amenities/<int:pk>", views.AmenityDetail.as_view()),
]