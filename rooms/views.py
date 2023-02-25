from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError
from rest_framework.status import HTTP_204_NO_CONTENT
from .models import Amenity, Room
from categories.models import Category
from .serializers import AmenitySerializer, RoomListSerializer, RoomDetailSerializer


#/api/v1/rooms/amenities
class Amenities(APIView):
    def get(self, request):
        all_amenities = Amenity.objects.all()
        serializer = AmenitySerializer(all_amenities, many=True)

        return Response(serializer.data)
    
    def post(self, request):
        if request.user.is_authenticated:
            serializer = AmenitySerializer(data=request.data)
            if serializer.is_valid():
                amenity = serializer.save(owner=request.user)
                return Response(AmenitySerializer(amenity).data)
            else:
                return Response(serializer.errors)
        else:
            raise NotAuthenticated

#/api/v1/rooms/amenities/1
class AmenityDetail(APIView):
    def get_object(self, pk):
        try:
            return Amenity.objects.get(pk=pk)
        except Amenity.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(amenity)

        return Response(serializer.data)

    def put(self, request, pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(amenity, data=request.data, partial=True)

        if serializer.is_valid():
            updated_amenity = serializer.save()
            return Response(AmenitySerializer(updated_amenity).data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        amenity = self.get_object(pk)
        amenity.delete()

        return Response(status=HTTP_204_NO_CONTENT)


class Rooms(APIView):
    def get(self, request):
        all_rooms = Room.objects.all()
        serializer = RoomListSerializer(all_rooms, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = RoomDetailSerializer(data=request.data)
        if serializer.is_valid():
            category_pk = request.data.get("category")

            if not category_pk:
                raise ParseError("Category is required.")
            try:
                category = Category.objects.get(pk=category_pk)
                if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                    raise ParseError("The category kind should be 'rooms'.")
            except Category.DoesNotExist:
                raise ParseError("Category not found")

            # room = serializer.save(
            #     owner=request.user,
            #     category=category
            # )

            amenity_list = list()
            amenities = request.data.get("amenities")
            for amenity_pk in amenities:
                try:
                    amenity = Amenity.objects.get(pk=amenity_pk)
                except Amenity.DoesNotExist:
                    # TODO@Ando: room을 delete할지, 우선 등록 후 수정하도록 유도할지는 생각해 봐야할 문제.
                    room.delete()
                    raise ParseError(f"Amenity with id {amenity_pk} not found.")
                # room.amenities.add(amenity)
                amenity_list.append(amenity)

            room = serializer.save(
                owner=request.user,
                category=category,
                amenities=amenity_list
            )

            serializer = RoomDetailSerializer(room)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class RoomDetail(APIView):
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk)
        serializer = RoomDetailSerializer(room)

        return Response(serializer.data)

