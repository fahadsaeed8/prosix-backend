from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from user_management_app.models import UserProfile
from user_management_app.threads import accept_reject_email, send_password_reset_email
from .serializers import DefaulttUserSerializer, UserSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
import threading
import threading
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework import filters
from django.conf import settings

User = get_user_model()

class GetUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = DefaulttUserSerializer(user)
        
        return Response({
            'success': True, 
            'response': {
                'data': serializer.data,
            }
        }, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        address = request.data.get('address', None)
        phone_number = request.data.get('phone_number', None)
        role = request.data.get('role', None)
        logo = request.data.get('logo', None)
        
        # Check if email is being updated
        if 'email' in data:
            if data['email'] != user.email:  # Only check if email is actually being changed
                if User.objects.filter(email=data['email']).exclude(pk=user.pk).exists():
                    return Response({
                        'success': False,
                        'response': {'message':'Email already exists!'},
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if username is being updated
        if 'username' in data:
            if data['username'] != user.username:  # Only check if username is actually being changed
                if User.objects.filter(username=data['username']).exclude(pk=user.pk).exists():
                    return Response({
                        'success': False,
                        'response': {'message':'Username already exists!'},

                    }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate and update user fields
        for field in ['first_name', 'last_name', 'email', 'username']:
            if field in data:
                setattr(user, field, data[field])
        
        try:
            user.full_clean()
            user.save()

            if not role:
                role = 'user'
            profile = UserProfile.objects.filter(user=user).first()
            if not profile:
                profile = UserProfile.objects.create(user=user, role=role)

            if address:
                profile.address = address
            if role:
                profile.role = role
            if phone_number:
                profile.phone_number = phone_number
            if logo:
                profile.logo = logo
            profile.save()
            # Return updated user data
            serializer = DefaulttUserSerializer(user)
            return Response({
                'success': True,
                'response': {
                    'message': 'Profile updated successfully.',
                    'data': serializer.data
                }
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response({
                'success': False,
                'response': {
                    {'message':str(e)}}                    
                    
            }, status=status.HTTP_400_BAD_REQUEST)

        

class UserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Extract data from request
        first_name = request.data.get('first_name')
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        role = request.data.get('role')
        phone_number = request.data.get('phone_number')
        address = request.data.get('address')
        is_admin = request.data.get('is_admin', False)
        
        # Validation
        if not first_name:
            return Response({
                "success": False, 
                'response': {'message': 'First name is required'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not email:
            return Response({
                "success": False, 
                'response': {'message': 'Email is required'}
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if not username:
            return Response({
                "success": False, 
                'response': {'message': 'Username is required'}
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if not password:
            return Response({
                "success": False, 
                'response': {'message': 'Password is required'}
            }, status=status.HTTP_400_BAD_REQUEST)

        if not confirm_password:
            return Response({
                "success": False, 
                'response': {'message': 'Confirm Password is required'}
            }, status=status.HTTP_400_BAD_REQUEST)

        if password != confirm_password:
            return Response({
                "success": False, 
                'response': {'message': 'Password and Confirm Password do not match'}
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({
                "success": False, 
                'response': {'message': 'Email already exists'}
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(username=username).exists():
            return Response({
                "success": False, 
                'response': {'message': 'Username already exists'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                password=password,
                is_active=False
            )
            if not role:
                role = 'user'

            profile = UserProfile.objects.create(user=user, role=role)
            if address:
                profile.address = address
            if phone_number:
                profile.phone_number = phone_number
            if is_admin:
                user.is_active = True
                user.save()
                profile.user_status = 'accepted'

                message = 'Congratulations! Your request has been successfully approved. You may now log in to your account and begin using our services.'

                try:
                    email_thread = threading.Thread(
                        target=accept_reject_email,
                        args=(user.email, message, 'Your profile is accepted')
                    )
                    email_thread.start()
                except:
                    return Response(
                        {'success': False, 'response': {'message': 'Failed to send email. Please try again later.'}},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            profile.save()

            if not is_admin:

                message = 'Your request is currently under review by our team. Please wait for approval. We appreciate your patience.'
                
                try:
                    email_thread = threading.Thread(
                        target=accept_reject_email,
                        args=(user.email, message, 'Your profile is currently under review')
                    )
                    email_thread.start()
                except:
                    return Response(
                        {'success': False, 'response': {'message': 'Failed to send email. Please try again later.'}},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                message = 'You have received a new user request – please review and take necessary action.'
                try:
                    email_thread = threading.Thread(
                        target=accept_reject_email,
                        args=(settings.EMAIL_HOST_USER, message, 'You have received new user request')
                    )
                    email_thread.start()
                except:
                    return Response(
                        {'success': False, 'response': {'message': 'Failed to send email. Please try again later.'}},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            serializer = UserSerializer(user)
            
            return Response({
                'success': True, 
                'response': {
                    'data': serializer.data,
                    'message': 'User created successfully'
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "success": False, 
                'response': {'message': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password')

        if not email:
            return Response(
                {"success": False, 'response': {'message': 'email/Username is required!'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not password:
            return Response(
                {"success": False, 'response': {'message': 'Password is required!'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        check_user = User.objects.filter(Q(email=email) | Q(username=email)).first()
        if not check_user:
            return Response(
                {"success": False, 'response': {'message': 'The entered username/email or password is incorrect. Please try again!'}},
                status=status.HTTP_404_NOT_FOUND
            )
            

            
        if check_user.is_active is False: 
            return Response(
                {"success": False, 'response': {'message': 'Sorry! Your account is not active!'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile = UserProfile.objects.filter(user=check_user).first()

        
        if profile: 
            if profile.user_status == 'pending':
                return Response(
                    {"success": False, 'response': {'message': 'Your request is currently under review by our team. Please wait for approval. We appreciate your patience.'}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if profile.user_status == 'rejected':
                return Response(
                    {"success": False, 'response': {'message': 'Your request has been declined due to an issue during review. For further clarification or assistance, please contact our support team.'}},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        user = authenticate(username=check_user.username, password=password)
        
        if not user:
            return Response(
                {"success": False, 'response': {'message': 'Incorrect Email or password'}},
                status=status.HTTP_403_FORBIDDEN
            )
            

        # Create or get token
        token, created = Token.objects.get_or_create(user=user)
        access_token = token.key
        serializer = DefaulttUserSerializer(user)


        return Response(
            {'success': True, 'response': {'data': serializer.data, 'access_token': access_token, 'message': 'Login successfully!'}},
            status=status.HTTP_200_OK
        )
    

class LogoutApiView(APIView):
    def post(self, request):            
        request.user.auth_token.delete()
        return Response({'success': True, 'response': {'message': 'User Logged Out Successfully'}},
                        status=status.HTTP_200_OK)
    

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email, is_active=True)
        except ObjectDoesNotExist:
            return Response(
                {'success': False, 'response': {'message': 'User with the given email address does not exist!'}},
                status=status.HTTP_404_NOT_FOUND)
        
        # Generating a new password - fixed line
        new_password = get_random_string(10)
        user.set_password(new_password)
        user.save()

        # Start a new thread to send the email
        try:
            email_thread = threading.Thread(
                target=send_password_reset_email,
                args=(email, new_password)
            )
            email_thread.start()
        except:
            return Response(
                {'success': False, 'response': {'message': 'Failed to send email. Please try again later.'}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({'success': True,
                         'response': {'message': 'Password has been reset and sent to your email.'}},
                        status=status.HTTP_200_OK)
    

class AssignUserPermissionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        role = request.data.get('role')
        user_id = request.data.get('user')
        permissions = request.data.get('permissions') 

        if not all([role, user_id, permissions]):
            return Response({
                'success': False,
                'response': {'message': 'Role, user and permissions are required'}
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_roles = ['user',  'designer', 'developer', 'customizer']  
        if role not in valid_roles:
            return Response({
                'success': False,
                'response': {'message': f'Invalid role specified. Valid roles are: {", ".join(valid_roles)}'}
            }, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(permissions, list):
            return Response({
                'success': False,
                'response': {'message': 'Permissions should be a list'}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'response': {'message': 'User does not exist'}
            }, status=status.HTTP_404_NOT_FOUND)

        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': role, 'permission': permissions}
        )

        if not created:
            profile.role = role
            profile.permission = permissions
            profile.save()

        return Response({
            'success': True,
            'response': {
                'message': 'Permissions set successfully!',
                'profile_id': profile.id,
                'created': created
            }
        }, status=status.HTTP_200_OK)


class UserListView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email', 'username']
    
    def get_queryset(self):
        queryset = User.objects.exclude(
            profile__role='admin'
        ).select_related('profile')
        return queryset

class UserStatusListView(ListAPIView):
    serializer_class = DefaulttUserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email', 'username']
    
    def get_queryset(self):
        status = self.request.query_params.get('status', 'pending')
        
        valid_statuses = ['pending', 'accepted', 'rejected']
        if status not in valid_statuses:
            status = 'pending'
        
        profile_ids = UserProfile.objects.filter(user_status=status).exclude(role='admin').order_by('-id').values_list('user')
        queryset = User.objects.filter(id__in=profile_ids).order_by('-date_joined').distinct()
        
        return queryset

    
class AcceptRejectUserView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        user_status = request.data.get('user_status')
        role = request.data.get('role')
        is_active = request.data.get('is_active')

        # Validate at least one field is provided
        if not any([role, user_status, is_active is not None]):
            return Response({
                'success': False,
                'response': {'message': 'At least one of role, user_status, or is_active is required'}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get user and profile
        user = User.objects.filter(id=id).first()
        if not user:
            return Response({
                'success': False,
                'response': {'message': 'User does not exist'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        profile = UserProfile.objects.filter(user=user).first()
        if not profile:
            return Response({
                'success': False,
                'response': {'message': 'User profile does not exist'}
            }, status=status.HTTP_404_NOT_FOUND)

        # Validate user_status
        if user_status:
            valid_statuses = ['pending', 'accepted', 'rejected']
            if user_status not in valid_statuses:
                return Response({
                    'success': False,
                    'response': {'message': f'Invalid status options'}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            profile.user_status = user_status
            if is_active is None:
                user.is_active = (user_status == 'accepted')

        # Validate role
        if role:
            valid_roles = ['user', 'designer', 'developer', 'customizer']
            if role not in valid_roles:
                return Response({
                    'success': False,
                    'response': {'message': f'Invalid role options'}
                }, status=status.HTTP_400_BAD_REQUEST)
            profile.role = role

        if is_active is not None:
            user.is_active = bool(is_active)

        user.save()
        profile.save()
        if user_status:
            if user_status == 'accepted':
                message = 'Congratulations! Your request has been successfully approved. You may now log in to your account and begin using our services.'
                prifle_status = 'Your profile is accepted'
            elif user_status == 'rejected':
                prifle_status = 'Your profile is rejected'
                message = 'Your request has been declined due to an issue during review. For further clarification or assistance, please contact our support team.'
            else:
                prifle_status = ''
                message = ''

            try:
                email_thread = threading.Thread(
                    target=accept_reject_email,
                    args=(user.email, message, prifle_status)
                )
                email_thread.start()
            except:
                return Response(
                    {'success': False, 'response': {'message': 'Failed to send email. Please try again later.'}},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response({
            'success': True,
            'response': {
                'message': 'User updated successfully',
            }
        }, status=status.HTTP_200_OK)