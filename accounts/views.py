from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Organization, User, Bucket
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    OrganizationSerializer,
)
from .permissions import IsOrganizationMember, IsOrganizationManager


# --------------------------
# AUTH VIEWS
# --------------------------

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


# --------------------------
# ORGANIZATION VIEWS
# --------------------------

class OrganizationDetailWithMembersView(generics.RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    lookup_url_kwarg = "org_id"


class OrganizationUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsOrganizationManager]
    lookup_url_kwarg = "org_id"


class CreateBucketView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationManager]

    def post(self, request, org_id):
        # Validate organization
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response(
                {"detail": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Enforce: requester must be org manager
        self.check_object_permissions(request, org)

        # Extract bucket name and optional endpoint from request data
        bucket_name = request.data.get("name")
        endpoint = request.data.get("endpoint")

        if not bucket_name or not endpoint:
            return Response(
                {"detail": "Both 'name' and 'endpoint' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure bucket does not already exist for this organization
        if Bucket.objects.filter(name=bucket_name, organization=org).exists():
            return Response(
                {"detail": "Bucket already exists for this organization."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create bucket
        bucket = Bucket.objects.create(
            name=bucket_name,
            endpoint=endpoint,
            organization=org,
            created_by=request.user
        )

        return Response(
            {
                "detail": "Bucket created successfully.",
                "bucket_id": bucket.id,
                "name": bucket.name,
                "endpoint": bucket.endpoint
            },
            status=status.HTTP_201_CREATED
        )

class AddOrRemoveUserFromOrganizationView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationManager]

    def post(self, request, org_id, user_id):
        org = Organization.objects.get(id=org_id)
        user = User.objects.get(id=user_id)

        # Enforce: requester must be the organization manager
        self.check_object_permissions(request, org)
        
        if user.organization_id is not None and user.organization_id != org.id:
            return Response(
                {
                  "detail": "User is not part of this organization."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if user.organization_id == org.id:
            return Response(
                {"details":"User is already part of the organization."},
                status = status.HTTP_400_BAD_REQUEST,
            )
        
        user.organization = org
        user.save()

        return Response(
            {"detail":"User added successfully"},
            status = status.HTTP_200_OK
        )

    def delete(self, request, org_id, user_id):
        org = Organization.objects.get(id=org_id)
        user = User.objects.get(id=user_id)

        # Enforce: requester must be the organization manager
        self.check_object_permissions(request, org)

        if user.organization_id != org.id:
            return Response(
                {"detail": "User is not part of this organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if org.manager_id == user.id:
            return Response(
                {"detail": "Cannot remove the organization manager."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.organization = None
        user.save()

        return Response(
            {"detail": "User removed successfully."},
            status=status.HTTP_200_OK,
        )



class CreateBucketView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationManager]

    def post(self, request, org_id):
        # Validate organization
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response(
                {"detail": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Enforce: requester must be org manager
        self.check_object_permissions(request, org)

        # Extract bucket name from request data
        bucket_name = request.data.get("name")
        if not bucket_name:
            return Response(
                {"detail": "Bucket 'name' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure bucket does not already exist for this organization
        if Bucket.objects.filter(name=bucket_name, organization=org).exists():
            return Response(
                {"detail": "Bucket already exists for this organization."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create bucket
        bucket = Bucket.objects.create(
            name=bucket_name,
            organization=org
        )

        return Response(
            {
                "detail": "Bucket created successfully.",
                "bucket_id": bucket.id,
                "name": bucket.name
            },
            status=status.HTTP_201_CREATED
        )