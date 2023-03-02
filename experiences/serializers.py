from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import SerializerMethodField

from .models import Perk, Experience

from wishlists.models import Wishlist
from users.serializers import TinyUserSerializer
from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer
from categories.serializers import CategorySerializer

class PerkSerializer(ModelSerializer):
    class Meta:
        model = Perk
        fields = "__all__"

class ExperienceListSerializer(ModelSerializer):
    rating = SerializerMethodField()
    is_host = SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model=Experience
        fields = (
            "pk",
            "country",
            "city",
            "name",
            "price",
            "address",
            "start",
            "end",
            "description",
            "rating",
            "is_host",
            "photos"
        )

    # 이처럼 DB에 없는 속성이라도 API를 통해 표현할 수 있음.
    def get_rating(self, experience):
        return experience.rating()

    def get_is_host(self, experience):
        request = self.context["request"]
        return experience.host == request.user

class ExperienceDetailSerializer(ModelSerializer):

    host = TinyUserSerializer(read_only=True)
    perks = PerkSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = SerializerMethodField()
    is_host = SerializerMethodField()
    is_liked = SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Experience
        fields = "__all__"
        # depth = 1

    def get_rating(self, experience):
        return experience.rating()

    def get_is_host(self, experience):
        request = self.context["request"]
        return experience.host == request.user

    def get_is_liked(self, experience):
        request = self.context["request"]
        return Wishlist.objects.filter(
            user=request.user,
            rooms__pk=experience.pk,
        ).exists()

