from django.conf import settings
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework.status import HTTP_204_NO_CONTENT
from .models import Perk, Experience
from .serializers import (
    PerkSerializer,
    ExperienceListSerializer,
    ExperienceDetailSerializer,
)

from bookings.models import Booking
from bookings.serializers import (
    PublicBookingSerializer,
    CreateExperienceBookingSerializer,
)
from categories.models import Category
from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer


# Create your views here.
class Experiences(APIView):
    def get(self, request):
        all_experience = Experience.objects.all()
        serializer = ExperienceListSerializer(
            all_experience, many=True, context={"request": request}
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = ExperienceDetailSerializer(data=request.data)
        if serializer.is_valid():
            category_pk = request.data.get("category")

            if not category_pk:
                raise ParseError("Category is required.")
            try:
                category = Category.objects.get(pk=category_pk)
                if category.kind == Category.CategoryKindChoices.ROOMS:
                    raise ParseError(
                        "The category kind should be 'experiences'."
                    )
            except Category.DoesNotExist:
                raise ParseError("Category not found")

            # Room과는 다른 방식으로 진행했음.
            perk_pks = request.data.get("perks")
            perks = list()
            if perk_pks:
                for perk_pk in perk_pks:
                    try:
                        perk = Perk.objects.get(pk=perk_pk)
                    except Exception:
                        raise ParseError("Perk not found")
                    perks.append(perk)

            experience = serializer.save(
                host=request.user,
                category=category,
                perks=perks,
            )
            serializer = ExperienceDetailSerializer(
                experience, context={"request": request}
            )
            return Response(serializer.data)

        else:
            return Response(serializer.errors)


class ExperienceDetail(APIView):
    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        experience = self.get_object(pk)
        serializer = ExperienceDetailSerializer(
            experience, context={"request": request}
        )

        return Response(serializer.data)

    def put(self, request, pk):
        experience = self.get_object(pk)

        if experience.host != request.user:
            raise PermissionDenied

        serializer = ExperienceDetailSerializer(
            experience,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        if serializer.is_valid():
            category = None
            category_pk = request.data.get("category")

            if category_pk:
                try:
                    category = Category.objects.get(pk=category_pk)
                    if category.kind == Category.CategoryKindChoices.ROOMS:
                        raise ParseError(
                            "The category kind should be 'experiences'."
                        )
                except Category.DoesNotExist:
                    raise ParseError("Category not found")

            # Room과는 다른 방식으로 진행했음.
            perk_pks = request.data.get("perks")
            perks = list()
            if perk_pks:
                for perk_pk in perk_pks:
                    try:
                        perk = Perk.objects.get(pk=perk_pk)
                    except Exception:
                        raise ParseError("Perk not found")
                    # TODO@Ando: 기존에 선택된 것에서 빼거나 추가하는 방식은 어떻게 구현하려나?
                    perks.append(perk)

            experience = serializer.save(
                host=request.user,
                category=category,
                perks=perks,
            )
            serializer = ExperienceDetailSerializer(
                experience, context={"request": request}
            )
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        experience = self.get_object(pk)

        if experience.host != request.user:
            raise PermissionDenied

        experience.delete()

        return Response(status=HTTP_204_NO_CONTENT)


class ExperienceReviews(APIView):

    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
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
        experience = self.get_object(pk)
        serializer = ReviewSerializer(
            experience.reviews.all()[start:end],
            many=True,
        )
        return Response(serializer.data)

    # TODO@Ando: 동일한 유저가 두 번 리뷰를 달 수 없도록 해야할 것 같다.
    def post(self, request, pk):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                user=request.user,
                experience=self.get_object(pk),
            )
            serializer = ReviewSerializer(review)
            return Response(serializer.data)


class ExperiencePhotos(APIView):

    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        experience = self.get_object(pk)
        # if not request.user.is_authenticated:
        #     raise NotAuthenticated
        if request.user != experience.host:
            raise PermissionDenied
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            # TODO@Ando: serializer.save는 database에 objects를 save하는 것도 포함인 것 같다.
            photo = serializer.save(experience=experience)
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


from datetime import datetime, timedelta


class ExperienceBookings(APIView):

    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        # TODO@Ando: 다양한 경우에 대한 자세한 로직 구현은 추후에 진행해 봅시다.

        try:
            query_date = request.query_params["date"]
            time_start = datetime.strptime(query_date, "%Y-%m-%d")
            time_end = time_start + timedelta(days=1) - timedelta(seconds=1)
            time_range = (time_start, time_end)
        except KeyError:
            # TODO@Ando: datetime.min으로 해서 각 도시에 맞게 시간 조정을 하다 보면 0001-01-01 00:00:00 이전의 시간으로 넘어갈 수 있고 이러면 에러가 발생함.
            time_start, time_end = (
                datetime.strptime("0001-01-31", "%Y-%m-%d"),
                datetime.max,
            )
            time_range = (time_start, time_end)
        except ValueError:
            time_start, time_end = (
                datetime.strptime("0001-01-31", "%Y-%m-%d"),
                datetime.max,
            )
            time_range = (time_start, time_end)

        experience = self.get_object(pk)
        # now = timezone.localtime(timezone.now()).date()

        # TODO@Ando: 근데 date_range로 찾을 때는 check_in__gt 기능이 활성화되면 안될 것 같다. 나중에 수정하기.
        bookings = Booking.objects.filter(
            experience=experience,
            kind=Booking.BookingKindChoices.EXPERIENCE,
            experience_time__range=time_range,
            # experience_time__gt=time_start,
            # experience_time__lt=time_end,
        )
        serializer = PublicBookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        experience = self.get_object(pk)
        serializer = CreateExperienceBookingSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save(
                experience=experience,
                user=request.user,  # TODO@Ando: user는 주석처리하면 DB 상에 저장이 안됨. (on_delete가 cascade인 것과 관련이 있을지도.)
                kind=Booking.BookingKindChoices.EXPERIENCE,
            )
            serializer = PublicBookingSerializer(booking)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    # TODO@Ando: ExperienceBookingsDetail에서 진행해야 합니다.
    # def delete(self, request, pk):
    #     experience = self.get_object(pk)

    #     booking = Booking.objects.filter(
    #         experience=experience,
    #         kind=Booking.BookingKindChoices.EXPERIENCE,
    #         user=request.user
    #     )

    #     booking.delete()

    #     return Response(status=HTTP_204_NO_CONTENT)


class ExperiencePerks(APIView):
    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
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
        expereince = self.get_object(pk)
        serializer = PerkSerializer(
            expereince.perks.all()[start:end],
            many=True,
        )
        return Response(serializer.data)


class Perks(APIView):
    def get(self, reqeust):
        all_perks = Perk.objects.all()
        serializer = PerkSerializer(all_perks, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = PerkSerializer(data=request.data)
        if serializer.is_valid():
            perk = serializer.save()
            return Response(PerkSerializer(perk).data)
        else:
            return Response(serializer.errors)


class PerkDetail(APIView):
    def get_object(self, pk):
        try:
            return Perk.objects.get(pk=pk)
        except Perk.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        perk = self.get_object(pk)
        serializer = PerkSerializer(perk)

        return Response(serializer.data)

    def put(self, request, pk):
        perk = self.get_object(pk)
        serializer = PerkSerializer(perk, data=request.data, partial=True)

        if serializer.is_valid():
            updated_perk = serializer.save()
            return Response(PerkSerializer(updated_perk).data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        perk = self.get_object(pk)
        perk.delete()

        return Response(status=HTTP_204_NO_CONTENT)
