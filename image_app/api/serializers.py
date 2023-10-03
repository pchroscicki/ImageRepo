import datetime

import pytz
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import FileExtensionValidator
from django.db import transaction
from rest_framework import serializers

from ImageRepository.settings import TIME_ZONE
from image_app.consts import ENTERPRISE, PREMIUM, BASIC
from image_app.models import Image, Tier, Thumbnail, ImageData


def allowed_user(user: User, obj):
    tz = pytz.timezone(TIME_ZONE)
    now = datetime.datetime.now(tz=tz)
    try:
        tier = Tier.objects.get(user=user)
        if tier.name.name == ENTERPRISE:
            return True
        elif tier.name.name == PREMIUM and obj.valid_until > now:
            return True
        elif tier.name.name == BASIC and isinstance(obj, Thumbnail) and obj.valid_until > now:
            return obj.height == 200
        return False
    except ObjectDoesNotExist:
        return False


class CreateImageDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageData
        fields = (
            "title",
        )


class ImageDataDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageData
        fields = (
            'title',
            'created_at'
        )


class ThumbnailsDetailSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Thumbnail
        fields = (
            "height",
            "width",
            "thumbnail_url",
            "valid_until"
        )

    def get_thumbnail_url(self, thumbnail_model: Thumbnail):
        request = self.context.get('request')
        if allowed_user(request.user, thumbnail_model):
            thumbnail_url = thumbnail_model.thumbnail.url
            return request.build_absolute_uri(thumbnail_url)
        return None


class ImageDetailSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    thumbnails = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = (
            "data",
            "image_url",
            "valid_until",
            "thumbnails",
        )

    def get_data(self, image_model: Image):
        return ImageDataDetailSerializer(image_model.image_data).data

    def get_image_url(self, image_model: Image):
        request = self.context.get('request')
        if allowed_user(request.user, image_model):
            img_url = image_model.image.url
            return request.build_absolute_uri(img_url)
        return None

    def get_thumbnails(self, image_model: Image):
        thumbnail_qs = Thumbnail.objects.filter(original_image=image_model)
        return ThumbnailsDetailSerializer(thumbnail_qs, many=True, context={"request": self.context.get("request")}).data


class CreateImageSerializer(serializers.ModelSerializer):
    data = CreateImageDataSerializer()
    valid_for = serializers.IntegerField(write_only=True, max_value=30000, min_value=300,
                                         help_text="seconds(between 300-30000)")
    image = serializers.ImageField(write_only=True,
                                   validators=[FileExtensionValidator(allowed_extensions=["jpg", "png"])], )

    class Meta:
        model = Image
        fields = (
            "data",
            "valid_for",
            "image",
        )

    @transaction.atomic
    def create(self, validated_data):
        image_data = validated_data.pop("data", {})
        image_data_instance = ImageData(user=self.context["user"], **image_data)
        image_data_instance.save()

        tz = pytz.timezone(TIME_ZONE)
        datetime_now = datetime.datetime.now(tz=tz)
        valid_for = datetime.timedelta(seconds=(validated_data["valid_for"]))
        validated_data["valid_until"] = datetime_now + valid_for
        validated_data.pop("valid_for", None)

        instance = Image.objects.create(image_data=image_data_instance, **validated_data)
        return instance
