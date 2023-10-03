from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.reverse import reverse
from image_app.api import serializers
from image_app.models import Image
from rest_framework import mixins, viewsets, permissions


class ImageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Image.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.CreateImageSerializer
        return serializers.ImageDetailSerializer

    def get_queryset(self):
        return Image.objects.filter(image_data__user=self.request.user)

    @extend_schema(
        description="This endpoint save the uploaded image with thumbnails and returns output with image data and links. The return output depends on user account tiers: Basic, Premium or Enterprise."
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"user": request.user})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return redirect(reverse("api:image-detail", args=[instance.image_data.uuid]))

    @extend_schema(
        description="This endpoint returns the list of all user's images"
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    @extend_schema(
        description="This endpoint returns the details of the created image and associated data and thumbnails."
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={"request": request})
        return Response(serializer.data)



