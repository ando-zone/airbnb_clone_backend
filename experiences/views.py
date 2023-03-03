from django.conf import settings

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

from categories.models import Category


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
