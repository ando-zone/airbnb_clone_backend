from django.urls import path
from .views import (
    PerkDetail,
    Perks,
    Experiences,
    ExperienceDetail,
    ExperiencePerks,
    ExperienceReviews,
    ExperiencePhotos,
    ExperienceBookings
)


urlpatterns = [
    path("", Experiences.as_view()),
    path("<int:pk>", ExperienceDetail.as_view()),
    path("<int:pk>/perks", ExperiencePerks.as_view()),
    path("perks/", Perks.as_view()),
    path("perks/<int:pk>", PerkDetail.as_view()),
    path("<int:pk>/reviews", ExperienceReviews.as_view()),
    path("<int:pk>/photos", ExperiencePhotos.as_view()),
    path("<int:pk>/bookings", ExperienceBookings.as_view()),
]
