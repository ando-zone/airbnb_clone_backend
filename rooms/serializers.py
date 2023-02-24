from rest_framework.serializers import ModelSerializer
from .models import Amenity, Room
from users.serializers import TinyUserSerializer
from categories.serializers import CategorySerializer


class AmenitySerializer(ModelSerializer):
    class Meta:
        model = Amenity
        fields = (
            "name",
            "description"
        )


class RoomListSerializer(ModelSerializer):
    class Meta:
        model=Room
        fields = (
            "pk",
            "name",
            "country",
            "city",
            "price"
        )


class RoomDetailSerializer(ModelSerializer):

    owner = TinyUserSerializer(read_only=True)
    amenities = AmenitySerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Room
        fields = "__all__"
        # depth = 1

    # create나 save 메서드의 self 다음 인자인 validated_data에 추가로 데이터를 추가해주고 싶다면 \
    # 해줘야할 것은 serializer.save()를 호출할 때 데이터를 추가해주는 것이다.
    # def create(self, validated_data):
    #     return Room.objects.create(**validated_data)
