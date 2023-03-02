from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError
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
