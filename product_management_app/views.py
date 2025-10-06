from rest_framework import generics
from .models import Shirt, ShirtCategory, ShirtSubCategory, UserShirt, FavoriteShirt
from .serializers import ShirtListSerializer, ShirtSerializer, ShirtCategorySerializer, ShirtSubCategorySerializer, UserShirtSerializer, FavoriteShirtSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count
import json

class ShirtCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ShirtCategory.objects.all().order_by('-created_at')
    serializer_class = ShirtCategorySerializer

class ShirtCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShirtCategory.objects.all()
    serializer_class = ShirtCategorySerializer

class ShirtSubCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ShirtSubCategory.objects.all().order_by('-created_at')
    serializer_class = ShirtSubCategorySerializer

class ShirtSubCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShirtSubCategory.objects.all()
    serializer_class = ShirtSubCategorySerializer
    
class ShirtListCreateView(generics.ListCreateAPIView):
    queryset = Shirt.objects.all()
    serializer_class = ShirtSerializer

class ShirtRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shirt.objects.all()
    serializer_class = ShirtSerializer


class UserShirtCreateAPIView(APIView):
    def patch(self, request, id):
        try:
            data = request.data
            
            if 'colors' not in data:
                raise ValueError("Colors data is required")
                
            if isinstance(data['colors'], str):
                try:
                    data['colors'] = json.loads(data['colors'])
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON format for colors")
            
            try:
                request._mutable = True
            except:
                pass

            request.data['user'] = request.user.id
            request.data['shirt'] = id
            serializer = UserShirtSerializer(data=data)
            
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response({
                'success': True, 
                'response': {
                    'data': serializer.data,
                    'message': 'User shirt created successfully'
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "success": False, 
                'response': {'message': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)
        


class UserShirtListAPIView(APIView):
    def get(self, request, *args, **kwargs):
            user = request.user
            shirts = Shirt.objects.all()
            serializer = ShirtListSerializer(shirts, many=True, context={'user': user})
            
            return Response({
                'success': True,
                'response': {
                    'data': serializer.data,
                    'message': 'All shirts (user has no saved shirts)'
                }
            }, status=status.HTTP_200_OK)
        


class FavoriteShirtAPIView(APIView):
    def post(self, request):
        user = request.user
        shirt_id = request.data.get('shirt_id')
        user_shirt_id = request.data.get('user_shirt_id')

        # Validate that at least one ID is provided
        if not any([shirt_id, user_shirt_id]):
            return Response({
                "success": False,
                'response': {'message': 'Either shirt_id or user_shirt_id must be provided'}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if favorite already exists
            favorite = FavoriteShirt.objects.filter(user=user)
            
            if shirt_id:
                shirt = Shirt.objects.get(id=shirt_id)
                favorite = favorite.filter(shirt=shirt)
            else:
                user_shirt = UserShirt.objects.get(id=user_shirt_id)
                favorite = favorite.filter(user_shirt=user_shirt)

            # If exists, remove it
            if favorite.exists():
                favorite.delete()
                return Response({
                    'success': True,
                    'response': {
                        'message': 'Shirt removed from favorites successfully',
                        'is_favorite': False
                    }
                }, status=status.HTTP_200_OK)
            
            # If doesn't exist, create it
            data = {}
            if shirt_id:
                data['shirt'] = shirt_id
            else:
                data['user_shirt'] = user_shirt_id

            serializer = FavoriteShirtSerializer(data=data, context={'request': request})
            
            if serializer.is_valid():
                serializer.save(user=user)
                return Response({
                    'success': True,
                    'response': {
                        'data': serializer.data,
                        'message': 'Shirt added to favorites successfully',
                        'is_favorite': True
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": False,
                    'response': {'message': serializer.errors}
                }, status=status.HTTP_400_BAD_REQUEST)

        except Shirt.DoesNotExist:
            return Response({
                "success": False,
                'response': {'message': 'Shirt not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        except UserShirt.DoesNotExist:
            return Response({
                "success": False,
                'response': {'message': 'User shirt not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                'response': {'message': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)