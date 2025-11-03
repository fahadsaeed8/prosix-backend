from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import WebsiteSettings, Banner, Blog, Testimonial, Product, Category
from .serializers import WebsiteSettingsSerializer, BannerSerializer, BlogSerializer, TestimonialSerializer, ProductSerializer, CategorySerializer
from django.core.exceptions import ValidationError


class WebsiteSettingsView(APIView):
    """Get and Update Website Settings"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current website settings"""
        try:
            settings = WebsiteSettings.get_settings()
            serializer = WebsiteSettingsSerializer(settings)
            return Response({
                'success': True,
                'response': {
                    'data': serializer.data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'response': {
                    'message': f'Error retrieving website settings: {str(e)}'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request):
        """Update website settings (partial update)"""
        try:
            settings = WebsiteSettings.get_settings()
            serializer = WebsiteSettingsSerializer(settings, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'response': {
                        'data': serializer.data,
                        'message': 'Website settings updated successfully'
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'response': {
                        'message': 'Validation error',
                        'errors': serializer.errors
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'response': {
                    'message': f'Error updating website settings: {str(e)}'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """Update website settings (full update)"""
        try:
            settings = WebsiteSettings.get_settings()
            serializer = WebsiteSettingsSerializer(settings, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'response': {
                        'data': serializer.data,
                        'message': 'Website settings updated successfully'
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'response': {
                        'message': 'Validation error',
                        'errors': serializer.errors
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'response': {
                    'message': f'Error updating website settings: {str(e)}'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NavigationMenuView(APIView):
    """Update and Delete Navigation Menu Items"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Add a new navigation menu item"""
        try:
            name = request.data.get('name')
            link = request.data.get('link')
            
            if not name or not link:
                return Response({
                    'success': False,
                    'response': {
                        'message': 'Both name and link are required'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            settings = WebsiteSettings.get_settings()
            navigation_menu = settings.navigation_menu or []
            
            # Generate ID for new item (max existing ID + 1, or 1 if empty)
            max_id = max([item.get('id', 0) for item in navigation_menu], default=0)
            new_id = max_id + 1
            
            # Add new item with ID
            navigation_menu.append({
                'id': new_id,
                'name': name,
                'link': link
            })
            
            settings.navigation_menu = navigation_menu
            settings.save()
            
            serializer = WebsiteSettingsSerializer(settings)
            return Response({
                'success': True,
                'response': {
                    'data': serializer.data,
                    'message': 'Navigation menu item added successfully'
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'response': {
                    'message': f'Error adding navigation menu item: {str(e)}'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        """Delete navigation menu items by array of IDs"""
        try:
            settings = WebsiteSettings.get_settings()
            navigation_menu = settings.navigation_menu or []
            
            if not navigation_menu:
                return Response({
                    'success': False,
                    'response': {
                        'message': 'Navigation menu is empty'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get array of IDs to delete
            ids_to_delete = request.data.get('ids', [])
            
            if not ids_to_delete:
                return Response({
                    'success': False,
                    'response': {
                        'message': 'ids array is required to delete navigation menu items'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not isinstance(ids_to_delete, list):
                return Response({
                    'success': False,
                    'response': {
                        'message': 'ids must be an array of integers'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Convert all to integers and validate
            try:
                ids_to_delete = [int(item_id) for item_id in ids_to_delete]
            except (ValueError, TypeError):
                return Response({
                    'success': False,
                    'response': {
                        'message': 'All ids must be valid integers'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create set for faster lookup
            ids_to_delete_set = set(ids_to_delete)
            
            # Get existing IDs
            existing_ids = {item.get('id') for item in navigation_menu if item.get('id') is not None}
            
            # Validate all IDs exist
            invalid_ids = ids_to_delete_set - existing_ids
            if invalid_ids:
                return Response({
                    'success': False,
                    'response': {
                        'message': f'Invalid IDs: {list(invalid_ids)}. These IDs do not exist in the navigation menu'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Filter out items to delete
            deleted_items = []
            updated_menu = []
            for item in navigation_menu:
                item_id = item.get('id')
                if item_id in ids_to_delete_set:
                    deleted_items.append(item)
                else:
                    updated_menu.append(item)
            
            settings.navigation_menu = updated_menu
            settings.save()
            
            serializer = WebsiteSettingsSerializer(settings)
            return Response({
                'success': True,
                'response': {
                    'data': serializer.data,
                    'message': f'{len(deleted_items)} navigation menu item(s) deleted successfully',
                    'deleted_items': [{'id': item.get('id'), 'name': item.get('name'), 'link': item.get('link')} for item in deleted_items]
                }
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'success': False,
                'response': {
                    'message': f'Error deleting navigation menu items: {str(e)}'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateNavigationMenuItemView(APIView):
    """Update navigation menu items by ID"""
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        """Update navigation menu items - receives all items with IDs and updates matching ones"""
        try:
            navigation_menu = request.data.get('navigation_menu')
            
            if navigation_menu is None:
                return Response({
                    'success': False,
                    'response': {
                        'message': 'navigation_menu array is required'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not isinstance(navigation_menu, list):
                return Response({
                    'success': False,
                    'response': {
                        'message': 'navigation_menu must be an array'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate each item structure
            for i, item in enumerate(navigation_menu):
                if not isinstance(item, dict):
                    return Response({
                        'success': False,
                        'response': {
                            'message': f'Navigation menu item at index {i} must be an object'
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if 'id' not in item:
                    return Response({
                        'success': False,
                        'response': {
                            'message': f'Navigation menu item at index {i} must have an "id" field'
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if not isinstance(item['id'], int):
                    return Response({
                        'success': False,
                        'response': {
                            'message': f'Navigation menu item at index {i} - "id" must be an integer'
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if 'name' not in item or 'link' not in item:
                    return Response({
                        'success': False,
                        'response': {
                            'message': f'Navigation menu item at index {i} must have both "name" and "link" fields'
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if not isinstance(item['name'], str) or not isinstance(item['link'], str):
                    return Response({
                        'success': False,
                        'response': {
                            'message': f'Navigation menu item at index {i} - "name" and "link" must be strings'
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get current settings
            settings = WebsiteSettings.get_settings()
            current_menu = settings.navigation_menu or []
            
            # Create a dictionary for quick lookup by ID
            menu_dict = {item.get('id'): item for item in current_menu}
            
            # Track which IDs are being updated
            updated_ids = set()
            new_items = []
            
            # Update existing items and collect new items
            for item in navigation_menu:
                item_id = item['id']
                
                if item_id in menu_dict:
                    # Update existing item
                    menu_dict[item_id] = {
                        'id': item_id,
                        'name': item['name'],
                        'link': item['link']
                    }
                    updated_ids.add(item_id)
                else:
                    # This is a new item (ID doesn't exist in current menu)
                    new_items.append({
                        'id': item_id,
                        'name': item['name'],
                        'link': item['link']
                    })
            
            # Rebuild navigation menu: existing items (updated) + new items
            updated_menu = []
            
            # Add all existing items (preserving order, updating where needed)
            for item in current_menu:
                item_id = item.get('id')
                if item_id in updated_ids:
                    # Replace with updated version
                    updated_menu.append(menu_dict[item_id])
                elif item_id is not None:
                    # Keep existing item as is
                    updated_menu.append(item)
            
            # Add new items
            updated_menu.extend(new_items)
            
            # Update settings
            settings.navigation_menu = updated_menu
            settings.save()
            
            serializer = WebsiteSettingsSerializer(settings)
            return Response({
                'success': True,
                'response': {
                    'data': serializer.data,
                    'message': f'Navigation menu updated successfully. {len(updated_ids)} item(s) updated, {len(new_items)} new item(s) added'
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'response': {
                    'message': f'Error updating navigation menu: {str(e)}'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BannerListCreateView(generics.ListCreateAPIView):
    """List all banners or create a new banner"""
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
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
                'message': 'Banner created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class BannerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a banner by ID"""
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
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
                'message': 'Banner updated successfully'
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
                'message': 'Banner deleted successfully'
            }
        }, status=status.HTTP_200_OK)


class BlogListCreateView(generics.ListCreateAPIView):
    """List all blogs or create a new blog"""
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
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
                'message': 'Blog created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class BlogRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a blog by ID"""
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
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
                'message': 'Blog updated successfully'
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
                'message': 'Blog deleted successfully'
            }
        }, status=status.HTTP_200_OK)


class TestimonialListCreateView(generics.ListCreateAPIView):
    """List all testimonials or create a new testimonial"""
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
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
                'message': 'Testimonial created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class TestimonialRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a testimonial by ID"""
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
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
                'message': 'Testimonial updated successfully'
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
                'message': 'Testimonial deleted successfully'
            }
        }, status=status.HTTP_200_OK)


class ProductListCreateView(generics.ListCreateAPIView):
    """List all products or create a new product"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
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
                'message': 'Product created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a product by ID"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
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
                'message': 'Product updated successfully'
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
                'message': 'Product deleted successfully'
            }
        }, status=status.HTTP_200_OK)


class CategoryListCreateView(generics.ListCreateAPIView):
    """List all categories or create a new category"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
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
                'message': 'Category created successfully'
            }
        }, status=status.HTTP_201_CREATED)


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a category by ID"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
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
                'message': 'Category updated successfully'
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
                'message': 'Category deleted successfully'
            }
        }, status=status.HTTP_200_OK)


class InventoryStatsAPIView(APIView):
    """Get inventory statistics"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Returns inventory statistics:
        - total_products
        - low_stock_items (returns 0 until stock field is added)
        - out_of_stock (returns 0 until stock field is added)
        - total_inventory_cost (returns 0 until stock/quantity field is added)
        """
        try:
            # Count total products
            total_products = Product.objects.count()
            
            # Stock-related fields don't exist yet, return 0
            low_stock_items = 0
            out_of_stock = 0
            total_inventory_cost = 0
            
            stats = {
                'total_products': total_products,
                'low_stock_items': low_stock_items,
                'out_of_stock': out_of_stock,
                'total_inventory_cost': total_inventory_cost
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
                    'message': f'Error retrieving inventory statistics: {str(e)}'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
