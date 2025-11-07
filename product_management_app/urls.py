from django.urls import path
from .views import FavoriteShirtAPIView, ShirtListCreateView, ShirtRetrieveUpdateDestroyView, ShirtCategoryListCreateView, ShirtCategoryRetrieveUpdateDestroyView, ShirtSubCategoryListCreateView, ShirtSubCategoryRetrieveUpdateDestroyView, UserShirtCreateAPIView, UserShirtListAPIView, CustomizerListCreateView, CustomizerRetrieveUpdateDestroyView, CustomizerStatisticsAPIView, PatternListCreateView, PatternRetrieveUpdateDestroyView, ColorListCreateView, ColorRetrieveUpdateDestroyView, FontListCreateView, FontRetrieveUpdateDestroyView, OrderListCreateView, OrderRetrieveUpdateDestroyView, InvoiceListCreateView, InvoiceRetrieveDestroyView, RevenueReportListCreateView, RevenueReportRetrieveUpdateDestroyView, ProductSalesReportListCreateView, ProductSalesReportRetrieveUpdateDestroyView, CustomerAnalysisReportListCreateView, CustomerAnalysisReportRetrieveUpdateDestroyView, GrowthTrendReportListCreateView, GrowthTrendReportRetrieveUpdateDestroyView, GenerateRevenueReportAPIView, GenerateProductSalesReportAPIView, GenerateCustomerAnalysisReportAPIView, GenerateGrowthTrendReportAPIView

urlpatterns = [
    
    path('shirtcategory/', ShirtCategoryListCreateView.as_view()),
    path('shirtcategory/<int:pk>/', ShirtCategoryRetrieveUpdateDestroyView.as_view()),

    path('shirtsubcategory/', ShirtSubCategoryListCreateView.as_view()),
    path('shirtsubcategory/<int:pk>/', ShirtSubCategoryRetrieveUpdateDestroyView.as_view()),

    path('shirts/', ShirtListCreateView.as_view()),
    path('shirts/<int:pk>/', ShirtRetrieveUpdateDestroyView.as_view()),
    path('customizeshirts/<int:id>/', UserShirtCreateAPIView.as_view()),
    path('usershirts/', UserShirtListAPIView.as_view()),
    path('favoriteshirt/', FavoriteShirtAPIView.as_view()),
    
    path('customizers/', CustomizerListCreateView.as_view()),
    path('customizers/<int:id>/', CustomizerRetrieveUpdateDestroyView.as_view()),
    path('customizers/statistics/', CustomizerStatisticsAPIView.as_view()),
    
    path('patterns/', PatternListCreateView.as_view()),
    path('patterns/<int:id>/', PatternRetrieveUpdateDestroyView.as_view()),
    
    path('colors/', ColorListCreateView.as_view()),
    path('colors/<int:id>/', ColorRetrieveUpdateDestroyView.as_view()),
    
    path('fonts/', FontListCreateView.as_view()),
    path('fonts/<int:id>/', FontRetrieveUpdateDestroyView.as_view()),
    
    path('orders/', OrderListCreateView.as_view()),
    path('orders/<int:id>/', OrderRetrieveUpdateDestroyView.as_view()),
    
    path('invoices/', InvoiceListCreateView.as_view()),
    path('invoices/<int:id>/', InvoiceRetrieveDestroyView.as_view()),
    
    path('reports/revenue/', RevenueReportListCreateView.as_view()),
    path('reports/revenue/<int:id>/', RevenueReportRetrieveUpdateDestroyView.as_view()),
    path('reports/revenue/generate/', GenerateRevenueReportAPIView.as_view()),
    
    path('reports/product-sales/', ProductSalesReportListCreateView.as_view()),
    path('reports/product-sales/<int:id>/', ProductSalesReportRetrieveUpdateDestroyView.as_view()),
    path('reports/product-sales/generate/', GenerateProductSalesReportAPIView.as_view()),
    
    path('reports/customer-analysis/', CustomerAnalysisReportListCreateView.as_view()),
    path('reports/customer-analysis/<int:id>/', CustomerAnalysisReportRetrieveUpdateDestroyView.as_view()),
    path('reports/customer-analysis/generate/', GenerateCustomerAnalysisReportAPIView.as_view()),
    
    path('reports/growth-trend/', GrowthTrendReportListCreateView.as_view()),
    path('reports/growth-trend/<int:id>/', GrowthTrendReportRetrieveUpdateDestroyView.as_view()),
    path('reports/growth-trend/generate/', GenerateGrowthTrendReportAPIView.as_view()),

]