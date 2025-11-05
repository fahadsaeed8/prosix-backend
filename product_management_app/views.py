from rest_framework import generics
from .models import Shirt, ShirtCategory, ShirtSubCategory, UserShirt, FavoriteShirt, Customizer, UserCustomizer, Pattern, Color, Font, Order, Invoice
from .serializers import ShirtListSerializer, ShirtSerializer, ShirtCategorySerializer, ShirtSubCategorySerializer, UserShirtSerializer, FavoriteShirtSerializer, CustomizerSerializer, PatternSerializer, ColorSerializer, FontSerializer, OrderSerializer, InvoiceSerializer
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


class CustomizerListCreateView(generics.ListCreateAPIView):
    """List all customizers or create a new customizer"""
    queryset = Customizer.objects.all()
    serializer_class = CustomizerSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'success': True,
            'response': {
                'data': response.data
            }
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'response': {
                'data': serializer.data,
                'message': 'Customizer created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class CustomizerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a customizer by ID"""
    queryset = Customizer.objects.all()
    serializer_class = CustomizerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            'success': True,
            'response': {
                'data': response.data
            }
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'response': {
                'data': serializer.data,
                'message': 'Customizer updated successfully'
            }
        }, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'response': {
                'message': 'Customizer deleted successfully'
            }
        }, status=status.HTTP_200_OK)


class CustomizerStatisticsAPIView(APIView):
    """Get customizer statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Returns customizer statistics:
        - total_models: Total number of customizer models
        - total_active_models: Total number of active customizer models
        - total_views: Sum of all views across all models
        - total_customizations: Total number of user customizations
        """
        try:
            # Count total models
            total_models = Customizer.objects.count()
            
            # Count active models
            total_active_models = Customizer.objects.filter(is_active=True).count()
            
            # Calculate total views: each model has 4 parts (front, back, left, right)
            # So total views = total_models × 4
            total_views = total_models * 4
            
            # Count total customizations
            total_customizations = UserCustomizer.objects.count()
            
            stats = {
                'total_models': total_models,
                'total_active_models': total_active_models,
                'total_views': total_views,
                'total_customizations': total_customizations
            }
            
            return Response({
                'success': True,
                'response': {
                    'data': stats
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'response': {
                    'message': f'Error retrieving customizer statistics: {str(e)}'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatternListCreateView(generics.ListCreateAPIView):
    """List all patterns or create a new pattern"""
    queryset = Pattern.objects.all()
    serializer_class = PatternSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'success': True,
            'response': {
                'data': response.data
            }
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'response': {
                'data': serializer.data,
                'message': 'Pattern created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class PatternRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a pattern by ID"""
    queryset = Pattern.objects.all()
    serializer_class = PatternSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            'success': True,
            'response': {
                'data': response.data
            }
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'response': {
                'data': serializer.data,
                'message': 'Pattern updated successfully'
            }
        }, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'response': {
                'message': 'Pattern deleted successfully'
            }
        }, status=status.HTTP_200_OK)


class ColorListCreateView(generics.ListCreateAPIView):
    """List all colors or create a new color"""
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'success': True,
            'response': {
                'data': response.data
            }
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'response': {
                'data': serializer.data,
                'message': 'Color created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class ColorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a color by ID"""
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            'success': True,
            'response': {
                'data': response.data
            }
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'response': {
                'data': serializer.data,
                'message': 'Color updated successfully'
            }
        }, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'response': {
                'message': 'Color deleted successfully'
            }
        }, status=status.HTTP_200_OK)


class FontListCreateView(generics.ListCreateAPIView):
    """List all fonts or create a new font"""
    queryset = Font.objects.all()
    serializer_class = FontSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'success': True,
            'response': {
                'data': response.data
            }
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'response': {
                'data': serializer.data,
                'message': 'Font created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class FontRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a font by ID"""
    queryset = Font.objects.all()
    serializer_class = FontSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            'success': True,
            'response': {
                'data': response.data
            }
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'response': {
                'data': serializer.data,
                'message': 'Font updated successfully'
            }
        }, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'response': {
                'message': 'Font deleted successfully'
            }
        }, status=status.HTTP_200_OK)


class OrderListCreateView(generics.ListCreateAPIView):
    """List all orders or create a new order"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'success': True,
            'response': {
                'data': response.data
            }
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'response': {
                'data': serializer.data,
                'message': 'Order created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an order by ID"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            'success': True,
            'response': {
                'data': response.data
            }
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'response': {
                'data': serializer.data,
                'message': 'Order updated successfully'
            }
        }, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'response': {
                'message': 'Order deleted successfully'
            }
        }, status=status.HTTP_200_OK)


class InvoiceListCreateView(generics.ListCreateAPIView):
    """List all invoices or create a new invoice"""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'success': True,
            'response': {
                'data': response.data
            }
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'response': {
                'data': serializer.data,
                'message': 'Invoice created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class InvoiceRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete an invoice by ID (no update allowed)"""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            'success': True,
            'response': {
                'data': response.data
            }
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'response': {
                'message': 'Invoice deleted successfully'
            }
        }, status=status.HTTP_200_OK)