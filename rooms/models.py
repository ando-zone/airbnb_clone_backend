from django.db import models
from common.models import CommonModel


class Room(CommonModel):

    """Room Model Definition"""

    class RoomKindChoices(models.TextChoices):
        ENTIRE_PLACE = ("entire_place", "Entire Place")
        PRIVATE_ROOM = ("private_room", "Private Room")
        SHARED_ROOM = "shared_room", "Shared Room"

    country = models.CharField(
        max_length=50,
        default="한국",
    )
    city = models.CharField(
        max_length=80,
        default="서울",
    )
    name = models.CharField(
        max_length=180,
        default="",
    )
    price = models.PositiveIntegerField()
    rooms = models.PositiveIntegerField()
    toilets = models.PositiveIntegerField()
    description = models.TextField()
    address = models.CharField(
        max_length=250,
    )
    pet_friendly = models.BooleanField(
        default=True,
    )
    kind = models.CharField(
        max_length=20,
        choices=RoomKindChoices.choices,
    )
    # 여기서 user는 owner를 뜻함. 예약자가 아님. 그래서 one to many입니다.
    # booking 그리고 그 안에 포함된 booker와 헷갈리면 안됩니다.
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="rooms",
    )
    amenities = models.ManyToManyField(
        "rooms.Amenity",
        related_name="rooms",
    )
    category = models.ForeignKey(
        "categories.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="rooms",
    )

    # def __str__(self):
    #     return self.name

    # TODO@Ando: 꼭 self가 아니어도 됨. 그냥 첫 번째 인수가 self가 되는 것.
    def __str__(room) -> str:
        return room.name

    def total_amenities(room):
        return room.amenities.count()

    def rating(room):
        count = room.reviews.count()
        if count == 0:
            return 0
        else:
            total_rating = 0
            for review in room.reviews.all().values("rating"):
                total_rating += review["rating"]
            return round(total_rating / count, 2)


class Amenity(CommonModel):

    """Amenity Definiton"""

    name = models.CharField(
        max_length=150,
    )
    description = models.CharField(
        max_length=150,
        null=True, # default = ""
        blank=True, #TODO@Ando what is this?
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Amenities"
