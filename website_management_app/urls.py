from django.urls import path
from .views import (
    WebsiteSettingsView, 
    NavigationMenuView, 
    UpdateNavigationMenuItemView,
    BannerListCreateView,
    BannerRetrieveUpdateDestroyView,
    BlogListCreateView,
    BlogRetrieveUpdateDestroyView,
    TestimonialListCreateView,
    TestimonialRetrieveUpdateDestroyView,
    ProductListCreateView,
    ProductRetrieveUpdateDestroyView,
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
    InventoryStatsAPIView
)

urlpatterns = [
    path('website-settings/', WebsiteSettingsView.as_view()),
    path('navigation-menu/', NavigationMenuView.as_view()),
    path('navigation-menu/update/', UpdateNavigationMenuItemView.as_view()),
    path('banners/', BannerListCreateView.as_view()),
    path('banners/<int:id>/', BannerRetrieveUpdateDestroyView.as_view()),
    path('blogs/', BlogListCreateView.as_view()),
    path('blogs/<int:id>/', BlogRetrieveUpdateDestroyView.as_view()),
    path('testimonials/', TestimonialListCreateView.as_view()),
    path('testimonials/<int:id>/', TestimonialRetrieveUpdateDestroyView.as_view()),
    path('products/', ProductListCreateView.as_view()),
    path('products/<int:id>/', ProductRetrieveUpdateDestroyView.as_view()),
    path('categories/', CategoryListCreateView.as_view()),
    path('categories/<int:id>/', CategoryRetrieveUpdateDestroyView.as_view()),
    path('inventory/stats/', InventoryStatsAPIView.as_view()),
]

