from django.urls import path
from mytig import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

urlpatterns = [
    path('onsaleproducts/', views.PromoList.as_view()),
    path('onsaleproduct/<int:tig_id>/', views.PromoDetail.as_view()),
    path('availableproducts/', views.AvailableList.as_view()),
    path('availableproduct/<int:tig_id>/', views.AvailableDetail.as_view()),
    path('infoproducts/', views.InfoProductList.as_view()),
    path('infoproduct/<int:tig_id>/', views.InfoProductDetail.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('update_product_stock/<int:tig_id>/', views.UpdateProductStock.as_view(), name='update_product_stock'),
    path('update_sale_percentage/<int:tig_id>/', views.UpdateProductSalePercentage.as_view(), name='update_product_sale_percentage'),
    path('products_by_category/<str:category>/', views.ProductsByCategory.as_view(), name='products_by_category'),
    path('update_multiple_product_stocks/', views.UpdateMultipleProductStocks.as_view(), name='update_multiple_product_stocks'),
    path('update_multiple_product_promotions/', views.UpdateMultipleProductPromotions.as_view(), name='update_multiple_product_promotions'),

]
