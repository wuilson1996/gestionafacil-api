from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^Create_Product/$',Create_Product,name="Create_Product"),
	url(r'^Update_Product/$',Update_Product,name="Update_Product"),
	url(r'^Delete_Product/$',Delete_Product,name="Delete_Product"),
	url(r'^Product_Reserved_User/$',Product_Reserved_User,name="Product_Reserved_User"),
	url(r'^Return_Products/$',Return_Products,name="Return_Products"),
	url(r'^return_product_UNIQUE/$',return_product_UNIQUE,name="return_product_UNIQUE"),
	url(r'^Get_Best_Selling_Product/$',Get_Best_Selling_Product,name="Get_Best_Selling_Product"),
	url(r'^Get_List_Best_Selling_Product/$',Get_List_Best_Selling_Product,name="Get_List_Best_Selling_Product"),
	url(r'^Get_All_List_Best_Selling_Product/$',Get_All_List_Best_Selling_Product,name="Get_All_List_Best_Selling_Product"),
	
	url(r'^Get_List_Products/$',Get_List_Products,name="Get_List_Products"),
	url(r'^Get_Product/$',Get_Product,name="Get_Product"),
	url(r'^Get_Category/$',Get_Category,name="Get_Category"),
	url(r'^Get_SubCategory/$',Get_SubCategory,name="Get_SubCategory"),
	url(r'^Get_List_Products_Supplier/$',Get_List_Products_Supplier,name="Get_List_Products_Supplier"),

	
	url(r'^Create_Supplier/$',Create_Supplier,name="Create_Supplier"),
	url(r'^Update_Supplier/$',Update_Supplier,name="Update_Supplier"),
	url(r'^Delete_Supplier/$',Delete_Supplier,name="Delete_Supplier"),
	url(r'^List_Supplier/$',List_Supplier,name="List_Supplier"),
	url(r'^Get_Supplier/$',Get_Supplier,name="Get_Supplier"),
]