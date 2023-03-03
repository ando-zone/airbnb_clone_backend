from django.urls import path
from .views import (
    PerkDetail,
    Perks,
    Experiences,
    ExperienceDetail,
    ExperiencePerks,
)


urlpatterns = [
    path("", Experiences.as_view()),
    path("<int:pk>", ExperienceDetail.as_view()),
    path("<int:pk>/perks", ExperiencePerks.as_view()),
    path("perks/", Perks.as_view()),
    path("perks/<int:pk>", PerkDetail.as_view()),
    # path("<int:pk>/reviews", views.RoomReviews.as_view()),
    # path("<int:pk>/photos", views.RoomPhotos.as_view()),
    # path("<int:pk>/bookings", views.RoomBookings.as_view()),
]
