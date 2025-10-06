from django.urls import path
from .views import FavoriteShirtAPIView, ShirtListCreateView, ShirtRetrieveUpdateDestroyView, ShirtCategoryListCreateView, ShirtCategoryRetrieveUpdateDestroyView, ShirtSubCategoryListCreateView, ShirtSubCategoryRetrieveUpdateDestroyView, UserShirtCreateAPIView, UserShirtListAPIView

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

]