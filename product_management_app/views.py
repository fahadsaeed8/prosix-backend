from rest_framework import generics, viewsets
from .models import Shirt, ShirtCategory, ShirtSubCategory, UserShirt, FavoriteShirt, Customizer, UserCustomizer, Pattern, Color, Font, Order, Invoice, RevenueReport, ProductSalesReport, CustomerAnalysisReport, GrowthTrendReport, ShirtDraft
from website_management_app.models import Category
from .serializers import ShirtListSerializer, ShirtSerializer, ShirtCategorySerializer, ShirtSubCategorySerializer, UserShirtSerializer, FavoriteShirtSerializer, CustomizerSerializer, PatternSerializer, ColorSerializer, FontSerializer, OrderSerializer, InvoiceSerializer, RevenueReportSerializer, ProductSalesReportSerializer, CustomerAnalysisReportSerializer, GrowthTrendReportSerializer, ShirtDraftSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from decimal import Decimal
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
    def create(self, request, *args, **kwargs):
        # Enforce optional category password protection
        category_id = request.data.get('category')
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({"category": ["Invalid category."]}, status=status.HTTP_400_BAD_REQUEST)
            if category.password:
                provided = request.data.get('category_password')
                if not provided:
                    provided = request.headers.get('X-Category-Password')
                if provided != category.password:
                    return Response({"category_password": ["Invalid or missing category password."]}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

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


# Revenue Report Views
class RevenueReportListCreateView(generics.ListCreateAPIView):
    """List all revenue reports or create a new revenue report"""
    queryset = RevenueReport.objects.all()
    serializer_class = RevenueReportSerializer
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
                'message': 'Revenue report created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class RevenueReportRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a revenue report by ID"""
    queryset = RevenueReport.objects.all()
    serializer_class = RevenueReportSerializer
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
                'message': 'Revenue report updated successfully'
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
                'message': 'Revenue report deleted successfully'
            }
        }, status=status.HTTP_200_OK)


# Product Sales Report Views
class ProductSalesReportListCreateView(generics.ListCreateAPIView):
    """List all product sales reports or create a new product sales report"""
    queryset = ProductSalesReport.objects.all()
    serializer_class = ProductSalesReportSerializer
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
                'message': 'Product sales report created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class ProductSalesReportRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a product sales report by ID"""
    queryset = ProductSalesReport.objects.all()
    serializer_class = ProductSalesReportSerializer
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
                'message': 'Product sales report updated successfully'
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
                'message': 'Product sales report deleted successfully'
            }
        }, status=status.HTTP_200_OK)


# Customer Analysis Report Views
class CustomerAnalysisReportListCreateView(generics.ListCreateAPIView):
    """List all customer analysis reports or create a new customer analysis report"""
    queryset = CustomerAnalysisReport.objects.all()
    serializer_class = CustomerAnalysisReportSerializer
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
                'message': 'Customer analysis report created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class CustomerAnalysisReportRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a customer analysis report by ID"""
    queryset = CustomerAnalysisReport.objects.all()
    serializer_class = CustomerAnalysisReportSerializer
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
                'message': 'Customer analysis report updated successfully'
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
                'message': 'Customer analysis report deleted successfully'
            }
        }, status=status.HTTP_200_OK)


# Growth Trend Report Views
class GrowthTrendReportListCreateView(generics.ListCreateAPIView):
    """List all growth trend reports or create a new growth trend report"""
    queryset = GrowthTrendReport.objects.all()
    serializer_class = GrowthTrendReportSerializer
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
                'message': 'Growth trend report created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class GrowthTrendReportRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a growth trend report by ID"""
    queryset = GrowthTrendReport.objects.all()
    serializer_class = GrowthTrendReportSerializer
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
                'message': 'Growth trend report updated successfully'
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
                'message': 'Growth trend report deleted successfully'
            }
        }, status=status.HTTP_200_OK)

class ShirtDraftViewSet(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView, viewsets.GenericViewSet):
    """
    ViewSet for ShirtDraft.
    Lookup by shirt_id instead of draft id.
    """
    queryset = ShirtDraft.objects.all()
    serializer_class = ShirtDraftSerializer
    lookup_field = 'shirt'

    def create(self, request, *args, **kwargs):
        # If a draft already exists for this shirt, update it instead of error
        shirt_id = request.data.get('shirt')
        if not shirt_id:
            return Response({"shirt": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        try:
            existing_draft = ShirtDraft.objects.get(shirt_id=shirt_id)
        except ShirtDraft.DoesNotExist:
            # No existing draft; create a new one
            return super().create(request, *args, **kwargs)
        # Existing draft found; perform an update with the incoming data
        serializer = self.get_serializer(existing_draft, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)



# Report Generation APIs
class GenerateRevenueReportAPIView(APIView):
    """Generate revenue report dynamically from Order and Invoice data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Generate revenue report with:
        - This month revenue (from completed orders and paid invoices)
        - Last month revenue
        - Growth percentage
        - Total orders count
        """
        try:
            now = timezone.now()
            current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_month_end = current_month_start - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Calculate this month revenue from completed orders
            this_month_orders = Order.objects.filter(
                date__gte=current_month_start,
                status='completed'
            )
            this_month_revenue_orders = this_month_orders.aggregate(
                total=Sum('total')
            )['total'] or Decimal('0.00')
            
            # Calculate this month revenue from paid invoices
            this_month_invoices = Invoice.objects.filter(
                date__gte=current_month_start,
                status='paid'
            )
            this_month_revenue_invoices = this_month_invoices.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            
            this_month_revenue = this_month_revenue_orders + this_month_revenue_invoices
            
            # Calculate last month revenue
            last_month_orders = Order.objects.filter(
                date__gte=last_month_start,
                date__lt=current_month_start,
                status='completed'
            )
            last_month_revenue_orders = last_month_orders.aggregate(
                total=Sum('total')
            )['total'] or Decimal('0.00')
            
            last_month_invoices = Invoice.objects.filter(
                date__gte=last_month_start,
                date__lt=current_month_start,
                status='paid'
            )
            last_month_revenue_invoices = last_month_invoices.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            
            last_month_revenue = last_month_revenue_orders + last_month_revenue_invoices
            
            # Calculate growth percentage
            if last_month_revenue > 0:
                growth_percentage = ((this_month_revenue - last_month_revenue) / last_month_revenue) * 100
            else:
                growth_percentage = Decimal('100.00') if this_month_revenue > 0 else Decimal('0.00')
            
            # Total orders count (this month)
            total_orders = this_month_orders.count()
            
            report_data = {
                'this_month_revenue': float(this_month_revenue),
                'last_month_revenue': float(last_month_revenue),
                'growth_percentage': float(growth_percentage),
                'total_orders': total_orders,
                'report_date': now.date(),
                'generated_at': now.isoformat()
            }
            
            return Response({
                'success': True,
                'response': {
                    'data': report_data,
                    'message': 'Revenue report generated successfully'
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'response': {
                    'message': f'Error generating revenue report: {str(e)}'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateProductSalesReportAPIView(APIView):
    """Generate product sales report dynamically from UserShirt and Customizer data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Generate product sales report with:
        - Top product name (most popular shirt or customizer)
        - Top product revenue (from orders)
        - Top product units sold (count of user shirts/customizers)
        - Top category
        """
        try:
            now = timezone.now()
            current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Get top shirt by user count
            top_shirt = Shirt.objects.annotate(
                user_count=Count('usershirts_shirt')
            ).order_by('-user_count').first()
            
            # Get top customizer by user count
            top_customizer = Customizer.objects.annotate(
                user_count=Count('usercustomizers_customizer')
            ).order_by('-user_count').first()
            
            # Determine top product
            if top_shirt and top_customizer:
                if top_shirt.user_count >= top_customizer.user_count:
                    top_product_name = top_shirt.name
                    top_product_units_sold = top_shirt.user_count
                    top_category = top_shirt.category.name if top_shirt.category else 'N/A'
                else:
                    top_product_name = top_customizer.model_name
                    top_product_units_sold = top_customizer.user_count
                    top_category = top_customizer.get_category_display()
            elif top_shirt:
                top_product_name = top_shirt.name
                top_product_units_sold = top_shirt.user_count
                top_category = top_shirt.category.name if top_shirt.category else 'N/A'
            elif top_customizer:
                top_product_name = top_customizer.model_name
                top_product_units_sold = top_customizer.user_count
                top_category = top_customizer.get_category_display()
            else:
                top_product_name = None
                top_product_units_sold = 0
                top_category = None
            
            # Calculate revenue from orders (this month) - approximate
            # Since we don't have direct product-order relationship, we'll use average order value
            this_month_orders = Order.objects.filter(
                date__gte=current_month_start,
                status='completed'
            )
            avg_order_value = this_month_orders.aggregate(
                avg=Avg('total')
            )['avg'] or Decimal('0.00')
            
            # Estimate top product revenue (units sold * average order value)
            top_product_revenue = Decimal(str(top_product_units_sold)) * avg_order_value if top_product_units_sold > 0 else Decimal('0.00')
            
            report_data = {
                'top_product_name': top_product_name,
                'top_product_revenue': float(top_product_revenue),
                'top_product_units_sold': top_product_units_sold,
                'top_category': top_category,
                'report_date': now.date(),
                'generated_at': now.isoformat()
            }
            
            return Response({
                'success': True,
                'response': {
                    'data': report_data,
                    'message': 'Product sales report generated successfully'
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'response': {
                    'message': f'Error generating product sales report: {str(e)}'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateCustomerAnalysisReportAPIView(APIView):
    """Generate customer analysis report dynamically from User and Order data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Generate customer analysis report with:
        - Total customers
        - New customers (this month)
        - Returning customers (customers with multiple orders)
        - Average order value
        """
        try:
            now = timezone.now()
            current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Total customers (users who have placed at least one order)
            total_customers = User.objects.filter(orders__isnull=False).distinct().count()
            
            # New customers (users who created their first order this month)
            all_customers = User.objects.filter(orders__isnull=False).distinct()
            new_customers = 0
            for customer in all_customers:
                first_order = customer.orders.order_by('date').first()
                if first_order and first_order.date >= current_month_start:
                    new_customers += 1
            
            # Returning customers (customers with more than one order)
            returning_customers = User.objects.annotate(
                order_count=Count('orders')
            ).filter(order_count__gt=1).count()
            
            # Average order value
            all_orders = Order.objects.filter(status='completed')
            avg_order_value = all_orders.aggregate(
                avg=Avg('total')
            )['avg'] or Decimal('0.00')
            
            report_data = {
                'total_customers': total_customers,
                'new_customers': new_customers,
                'returning_customers': returning_customers,
                'average_order_value': float(avg_order_value),
                'report_date': now.date(),
                'generated_at': now.isoformat()
            }
            
            return Response({
                'success': True,
                'response': {
                    'data': report_data,
                    'message': 'Customer analysis report generated successfully'
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'response': {
                    'message': f'Error generating customer analysis report: {str(e)}'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateGrowthTrendReportAPIView(APIView):
    """Generate growth trend report dynamically from historical Order and Invoice data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Generate growth trend report with:
        - Monthly growth percentage
        - Yearly growth percentage
        - Quarterly growth percentage
        - Market share (estimated)
        """
        try:
            now = timezone.now()
            current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_month_start = (current_month_start - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Current quarter start
            current_quarter = (now.month - 1) // 3
            current_quarter_start = now.replace(month=current_quarter * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Last quarter calculation
            if current_quarter == 0:
                # If current quarter is Q1, last quarter is Q4 of previous year
                last_quarter_start = now.replace(year=now.year - 1, month=10, day=1, hour=0, minute=0, second=0, microsecond=0)
                last_quarter_end = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            else:
                # Previous quarter of same year
                last_quarter_month = (current_quarter - 1) * 3 + 1
                last_quarter_start = now.replace(month=last_quarter_month, day=1, hour=0, minute=0, second=0, microsecond=0)
                last_quarter_end = current_quarter_start - timedelta(days=1)
            
            # Current year start
            current_year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            last_year_start = current_year_start.replace(year=current_year_start.year - 1)
            last_year_end = current_year_start - timedelta(days=1)
            
            # Monthly growth
            this_month_revenue = self._calculate_revenue(current_month_start, now)
            last_month_revenue = self._calculate_revenue(last_month_start, current_month_start - timedelta(days=1))
            monthly_growth = self._calculate_growth_percentage(this_month_revenue, last_month_revenue)
            
            # Quarterly growth
            this_quarter_revenue = self._calculate_revenue(current_quarter_start, now)
            last_quarter_revenue = self._calculate_revenue(
                last_quarter_start,
                last_quarter_end
            )
            quarterly_growth = self._calculate_growth_percentage(this_quarter_revenue, last_quarter_revenue)
            
            # Yearly growth
            this_year_revenue = self._calculate_revenue(current_year_start, now)
            last_year_revenue = self._calculate_revenue(last_year_start, last_year_end)
            yearly_growth = self._calculate_growth_percentage(this_year_revenue, last_year_revenue)
            
            # Market share (estimated as percentage of total revenue vs previous period)
            # This is a simplified calculation
            total_revenue_all_time = self._calculate_revenue(None, now)
            market_share = Decimal('100.00')  # Placeholder - would need industry data for real calculation
            
            report_data = {
                'monthly_growth': float(monthly_growth),
                'yearly_growth': float(yearly_growth),
                'quarterly_growth': float(quarterly_growth),
                'market_share': float(market_share),
                'report_date': now.date(),
                'generated_at': now.isoformat()
            }
            
            return Response({
                'success': True,
                'response': {
                    'data': report_data,
                    'message': 'Growth trend report generated successfully'
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'response': {
                    'message': f'Error generating growth trend report: {str(e)}'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _calculate_revenue(self, start_date, end_date):
        """Helper method to calculate revenue from orders and invoices"""
        orders_query = Order.objects.filter(status='completed')
        invoices_query = Invoice.objects.filter(status='paid')
        
        if start_date:
            orders_query = orders_query.filter(date__gte=start_date)
            invoices_query = invoices_query.filter(date__gte=start_date)
        
        if end_date:
            orders_query = orders_query.filter(date__lte=end_date)
            invoices_query = invoices_query.filter(date__lte=end_date)
        
        orders_revenue = orders_query.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        invoices_revenue = invoices_query.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        return orders_revenue + invoices_revenue
    
    def _calculate_growth_percentage(self, current, previous):
        """Helper method to calculate growth percentage"""
        if previous > 0:
            return ((current - previous) / previous) * 100
        else:
            return Decimal('100.00') if current > 0 else Decimal('0.00')
