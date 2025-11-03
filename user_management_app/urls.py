from django.urls import path
from .views import (
    AcceptRejectUserView, AssignUserPermissionView, UserAPIView, GetUserAPIView, 
    LoginView, LogoutApiView, ForgotPasswordView, UserListView, UserStatusListView, 
    StatisticsAPIView, MembershipStatsAPIView, MembersListAPIView
)

urlpatterns = [
    path('GetProfile', GetUserAPIView.as_view()),
    path('EditProfile/', GetUserAPIView.as_view()),
    path('SignUp/', UserAPIView.as_view()),
    path('Login/', LoginView.as_view()),
    path('Logout/', LogoutApiView.as_view()),
    path('ForgotPassword/', ForgotPasswordView.as_view()),
    path('AssignUserPermission/', AssignUserPermissionView.as_view()),
    path('UserList/', UserListView.as_view()),
    path('Statistics/', StatisticsAPIView.as_view()),
    path('MembershipStats/', MembershipStatsAPIView.as_view()),
    path('Members/', MembersListAPIView.as_view()),

    path('AcceptRejectUser/<int:id>/', AcceptRejectUserView.as_view()),
    path('UserStatusList/', UserStatusListView.as_view()),
]