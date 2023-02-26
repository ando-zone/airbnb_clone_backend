from django.db import transaction
from django.conf import settings
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError, PermissionDenied
from rest_framework.status import HTTP_204_NO_CONTENT
from reviews.serializers import ReviewSerializer
from .models import Amenity, Room
from categories.models import Category
from .serializers import AmenitySerializer, RoomListSerializer, RoomDetailSerializer
from medias.serializers import PhotoSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from bookings.models import Booking
from bookings.serializers import PublicBookingSerializer, CreateRoomBookingSerializer


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

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_rooms = Room.objects.all()
        serializer = RoomListSerializer(all_rooms, many=True, context={"request": request})

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

            # 아래가 좋은 코드인지 잘 모르겠다. 예외처리가 우선 분명하지 않고 indentation이 과도하게 많음.
            try:
                with transaction.atomic():
                    room = serializer.save(
                        owner=request.user,
                        category=category,
                    )
                    amenities = request.data.get("amenities")
                    for amenity_pk in amenities:
                        amenity = Amenity.objects.get(pk=amenity_pk)
                        room.amenities.add(amenity)
                    serializer = RoomDetailSerializer(room)
                    return Response(serializer.data)
            except Exception:
                raise ParseError("Amenity not found")
        else:
            return Response(serializer.errors)


class RoomDetail(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk)
        serializer = RoomDetailSerializer(room, context={"request": request})

        return Response(serializer.data)

    def put(self, request, pk):
        room = self.get_object(pk)
        
        # if not request.user.is_authenticated:
        #     raise NotAuthenticated

        if room.owner != request.user:
            raise PermissionDenied

        # TODO@Ando: code challenge with 'partial update' function
        serializer = RoomDetailSerializer(room, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            category = None
            category_pk = request.data.get("category")

            if category_pk:
                try:
                    category = Category.objects.get(pk=category_pk)
                    if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                        raise ParseError("The category kind should be 'rooms'.")
                except Category.DoesNotExist:
                    raise ParseError("Category not found")

            # TODO@Ando: try, except 구조 변경하기.
            # 아래가 좋은 코드인지 잘 모르겠다. 예외처리가 우선 분명하지 않고 indentation이 과도하게 많음.
            # 역시나... 예외처리가 불분명함. context 때문에 발생한 에러인데 파악하기가 어려움.
            try:
                with transaction.atomic():
                    room = serializer.save(owner=request.user)

                    if category is not None:
                        room = serializer.save(category=category)

                    amenities = request.data.get("amenities")

                    if amenities:
                        for amenity_pk in amenities:
                            amenity = Amenity.objects.get(pk=amenity_pk)
                            room.amenities.add(amenity)

                    serializer = RoomDetailSerializer(room, context={"request": request})
                    return Response(serializer.data)
            except Exception:
                raise ParseError("Amenity not found")
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        room = self.get_object(pk)

        # if not request.user.is_authenticated:
        #     raise NotAuthenticated

        if room.owner != request.user:
            raise PermissionDenied

        room.delete()

        return Response(status=HTTP_204_NO_CONTENT)


class RoomReviews(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            # TODO@Ando: page가 마지막 페이지를 넘어가면 마지막 페이지를 보여주는 것도 좋을 것 같다.
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        room = self.get_object(pk)
        serializer = ReviewSerializer(
            room.reviews.all()[start:end],
            many=True,
        )
        return Response(serializer.data)

    def post(self, request, pk):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                user=request.user,
                room=self.get_object(pk),
            )
            serializer = ReviewSerializer(review)
            return Response(serializer.data)


class RoomAmenities(APIView):
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            # TODO@Ando: page가 마지막 페이지를 넘어가면 마지막 페이지를 보여주는 것도 좋을 것 같다.
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        room = self.get_object(pk)
        serializer = AmenitySerializer(
            room.amenities.all()[start:end],
            many=True,
        )
        return Response(serializer.data)


class RoomPhotos(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        room = self.get_object(pk)
        # if not request.user.is_authenticated:
        #     raise NotAuthenticated
        if request.user != room.owner:
            raise PermissionDenied
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(room=room)
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

from datetime import datetime, timedelta
from dateutil import relativedelta

def getMonthRange(year, month):
    this_month_1st_day = datetime(year=year, month=month, day=1).date()
    next_month_1st_day = this_month_1st_day + relativedelta.relativedelta(months=1)

    this_month_last_day = next_month_1st_day - timedelta(days=1)

    return (this_month_1st_day, this_month_last_day)

class RoomBookings(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except:
            raise NotFound

    def get(self, request, pk):
        today_date = timezone.now().today()
        today_Y_M = f"{today_date.year}_{today_date.month}"

        try:
            today_date = timezone.now().today()
            today_Y_M = f"{today_date.year}_{today_date.month}"
            year_month = request.query_params.get("year_month", "No_input")

        except ValueError:
            year_month = "Wrong_input"

        room = self.get_object(pk)
        now = timezone.localtime(timezone.now()).date()

        if year_month == "No_input" or year_month == "Wrong_input":
            date_range = (datetime.min, datetime.max)
        else:
            year, month = year_month.split("_")
            date_range = getMonthRange(int(year), int(month))

        # TODO@Ando: 근데 date_range로 찾을 때는 check_in__gt 기능이 활성화되면 안될 것 같다. 나중에 수정하기.
        bookings = Booking.objects.filter(
            room=room,
            kind=Booking.BookingKindChoices.ROOM,
            check_in__range = date_range,
            check_in__gt=now,
        )
        serializer = PublicBookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        room = self.get_object(pk)
        serializer = CreateRoomBookingSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save(
                room=room,
                user=request.user, # user는 주석처리하면 DB 상에 저장이 안됨. (on_delete가 cascade인 것과 관련이 있을지도.)
                kind=Booking.BookingKindChoices.ROOM,
            )
            serializer = PublicBookingSerializer(booking)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)