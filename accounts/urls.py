from django.urls import path
from .views import SignupView, LoginView, OrganizationDetailWithMembersView, AddOrRemoveUserFromOrganizationView, OrganizationUpdateView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path('organizations/<int:org_id>/details/', OrganizationDetailWithMembersView.as_view()),
    path('organizations/<int:org_id>/update/', OrganizationUpdateView.as_view()),
    path('organizations/<int:org_id>/users/<int:user_id>/', AddOrRemoveUserFromOrganizationView.as_view())
]
