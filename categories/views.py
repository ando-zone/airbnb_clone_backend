# from rest_framework.decorators import api_view
# from rest_framework.exceptions import NotFound
# from rest_framework.response import Response
# from rest_framework.status import HTTP_204_NO_CONTENT
# from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

# Version 3)
# class Categories(APIView):

#     def get(self, request):
#         all_categories = Category.objects.all()
#         serializer = CategorySerializer(all_categories, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = CategorySerializer(data=request.data)
#         if serializer.is_valid():
#             new_category = serializer.save()
#             return Response(
#                 CategorySerializer(new_category).data,
#             )
#         else:
#             return Response(serializer.errors)

# # Version 2)
# # # Create your views here.
# # @api_view(["GET", "POST"])
# # def categories(request):

# #     if request.method == "GET":
# #         all_categories = Category.objects.all()
# #         serializer = CategorySerializer(all_categories, many=True)
# #         return Response(serializer.data)
# #     elif request.method == "POST":
# #         # 사용자를 100%로 신뢰하는 경우. 잘못 되었을 경우, 에러 발생.
# #         # Category.objects.create(
# #         #     name=request.data["name"],
# #         #     kind=request.data["kind"],
# #         # )
# #         # return Response({"created": True})

# #         # 사용자에 의존하지 않음. 에러 발생시키지 않고 JSON response로 잘못 입력했음을 알려줌.
# #         serializer = CategorySerializer(data=request.data)
# #         if serializer.is_valid():
# #             # return Response({"created": True})
# #             # .save()가 적절하게 create하거나 update 함.
# #             new_category = serializer.save()
# #             return Response(
# #                 CategorySerializer(new_category).data,
# #             )
# #         else:
# #             return Response(serializer.errors)

# #     # Version 1)
# #     # all_categories = Category.objects.all()
# #     # serializer = CategorySerializer(all_categories, many=True)
# #     # # single_category = Category.objects.get(pk=1)
# #     # # serializer = CategorySerializer(single_category)
# #     # return Response(
# #     #     {
# #     #         "ok": True,
# #     #         # "categories": Category.objects.all(),
# #     #         "categories": serializer.data,
# #     #     }
# #     # )

# Version 3)
# class CategoryDetail(APIView):
#     def get_object(self, pk):
#         try:
#             return Category.objects.get(pk=pk)
#         except Category.DoesNotExist:
#             raise NotFound

#     def get(self, request, pk):
#         serializer = CategorySerializer(self.get_object(pk))
#         return Response(serializer.data)

#     def put(self, request, pk):
#         serializer = CategorySerializer(
#             self.get_object(pk),
#             data=request.data,
#             partial=True,
#         )
#         if serializer.is_valid():
#             updated_category = serializer.save()
#             return Response(CategorySerializer(updated_category).data)
#         else:
#             return Response(serializer.errors)

#     def delete(self, request, pk):
#         self.get_object(pk).delete()
#         return Response(status=HTTP_204_NO_CONTENT)

# # Version 2)
# # @api_view(["GET", "PUT", "DELETE"])
# # def category(request, pk):
# #     try:
# #         category = Category.objects.get(pk=pk)
# #     except Category.DoesNotExist:
# #         raise NotFound

# #     if request.method == "GET":
# #         serializer = CategorySerializer(category)
# #         return Response(serializer.data)
# #     elif request.method == "PUT":
# #         # create할 때와는 다르게 CategorySerializer 인자에 두개가 들어감, partial은 제외하고
# #         # category는 원래 것, 그리고 data는 수정할 것.
# #         # 따라서 알아서 def update를 실행시키는구나를 인지함. save() 메서드가.
# #         serializer = CategorySerializer(
# #             category,
# #             data=request.data,
# #             partial=True,
# #         )
# #         if serializer.is_valid():
# #             updated_category = serializer.save()
# #             return Response(CategorySerializer(updated_category).data)
# #         else:
# #             return Response(serializer.errors)
# #     elif request.method == "DELETE":
# #         category.delete()
# #         return Response(status=HTTP_204_NO_CONTENT)
    
# #     # Version 1)
# #     # category = Category.objects.get(pk=pk)
# #     # serializer = CategorySerializer(category)
# #     # return Response(serializer.data)