from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer


# Create your views here.
@api_view(["GET", "POST"])
def categories(request):

    if request.method == "GET":
        all_categories = Category.objects.all()
        serializer = CategorySerializer(all_categories, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        # 사용자를 100%로 신뢰하는 경우. 잘못 되었을 경우, 에러 발생.
        # Category.objects.create(
        #     name=request.data["name"],
        #     kind=request.data["kind"],
        # )
        # return Response({"created": True})

        # 사용자에 의존하지 않음. 에러 발생시키지 않고 JSON response로 잘못 입력했음을 알려줌.
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            return Response({"created": True})
        else:
            return Response(serializer.errors)

    # Version 1)
    # all_categories = Category.objects.all()
    # serializer = CategorySerializer(all_categories, many=True)
    # # single_category = Category.objects.get(pk=1)
    # # serializer = CategorySerializer(single_category)
    # return Response(
    #     {
    #         "ok": True,
    #         # "categories": Category.objects.all(),
    #         "categories": serializer.data,
    #     }
    # )

@api_view()
def category(request, pk):
    category = Category.objects.get(pk=pk)
    serializer = CategorySerializer(category)
    return Response(serializer.data)