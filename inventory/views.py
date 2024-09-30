from rest_framework.response import Response
from django.shortcuts import render
from .models import *
from rest_framework.decorators import api_view

# Supplier
@api_view(['POST'])
def Create_Supplier(request):
    return Response(Supplier.create_supplier(request.data))

@api_view(['GET'])
def List_Supplier(request):
    return Response(Supplier.list_supplier(request.data))

@api_view(['POST'])
def Delete_Supplier(request):
    return Response(Supplier.delete_supplier(request.data))

@api_view(['GET'])
def Get_Supplier(request):
    return Response(Supplier.get_supplier(request.data))


# Product
@api_view(['POST'])
def Create_Product(request):
    return Response(Product.create_product(request.data))

@api_view(['DELETE'])
def Delete_Product(request):
    return Response(Product.delete_product(request.data))

@api_view(['GET'])
def Get_List_Products(request):
    return Response(Product.get_list_products(request.data))

@api_view(['GET'])
def Get_Product(request):
    return Response(Product.get_product(request.data))

@api_view(['GET'])
def Get_List_Products_Supplier(request):
    return Response(Product.get_list_products_supplier(request.data))

@api_view(['POST'])
def Product_Reserved_User(request):
    return Response(Product_Reserved.reserveding_product(request.data))

@api_view(['POST'])
def Return_Products(request):
    return Response(Product_Reserved.return_products(request.data['pk_user']))

@api_view(['PUT'])
def return_product_UNIQUE(request):
    return Response(Product_Reserved.return_product_unique(request.data))

@api_view(['GET'])
def Get_Best_Selling_Product(request):
    return Response(Best_Selling_Product.get_best_selling_product(request.data))

@api_view(['GET'])
def Get_List_Best_Selling_Product(request):
    return Response(Best_Selling_Product.get_list_best_selling_product(request.data))

@api_view(['GET'])
def Get_All_List_Best_Selling_Product(request):
    return Response(Best_Selling_Product.get_all_list_best_selling_product(request.data))


# Category
@api_view(['GET'])
def Get_Category(request):
    return Response(Category.get_list_category())

@api_view(['POST'])
def Get_SubCategory(request):
    return Response(SubCategory.get_list_subcategory(request.data))

@api_view(['GET'])
def Get_SubCategoryByBranch(request):
    return Response(SubCategory.get_list_subcategory_by_branch(request.data))

@api_view(['POST'])
def Create_SubCategoryByBranch(request):
    return Response(SubCategory.create_subcategory_by_branch(request.data))

@api_view(['DELETE'])
def Delete_SubCategoryByBranch(request):
    return Response(SubCategory.delete_subcategory_by_branch(request.data))