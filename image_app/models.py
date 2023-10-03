import uuid
import os
from PIL import Image as Img

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from rest_framework.reverse import reverse
from ImageRepository.settings import MEDIA_ROOT
from image_app.mixins import BaseModelMixin


def image_path(instance: "Image", filename: str) -> str:
    user_id = instance.image_data.user.id
    uuid = instance.image_data.uuid
    return f"{user_id}/{uuid}/original/{filename}"


def thumbnail_path(instance: "Thumbnail", filename: str) -> str:
    user_id = instance.original_image.image_data.user.id
    uuid = instance.original_image.image_data.uuid
    return f"{user_id}/{uuid}/thumbnails/{instance.width}_{instance.height}_{filename}"


def thumbnail_arbitrary_path(instance: "Image", filename: str) -> str:
    return f"{instance.user.id}/arbitrary/{instance.uuid}/{filename}"


class ImageData(BaseModelMixin):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
    )
    title = models.CharField(max_length=200, null=True, blank=True)
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Image(BaseModelMixin):
    image_data = models.OneToOneField(ImageData, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(
        upload_to=image_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "png"]
            )
        ],
    )
    valid_until = models.DateTimeField()


    @property
    def image_url(self):
        return reverse("original_image", args=(str(self.image_data.uuid),))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        original_image_data = self.image_data
        file_path = f"{original_image_data.user.id}/{original_image_data.uuid}/thumbnails/"

        if not os.path.exists(MEDIA_ROOT + "/" + file_path):
            os.mkdir(MEDIA_ROOT + "/" + file_path)

        file_name_200 = f'{200}_{200}_{self.image.name.split("/")[-1]}'
        image_original = Img.open(MEDIA_ROOT + "/" + self.image.name)
        image_original.thumbnail((200, 200))
        image_original.save(MEDIA_ROOT + "/" + file_path + file_name_200, quality=88)
        Thumbnail.objects.create(
            original_image=self,
            height=200,
            width=200,
            thumbnail=file_path + file_name_200,
            valid_until=self.valid_until
        )

        file_name_400 = f'{400}_{400}_{self.image.name.split("/")[-1]}'
        image_original_400 = Img.open(MEDIA_ROOT + "/" + self.image.name)
        image_original_400.thumbnail((400, 400))
        image_original_400.save(MEDIA_ROOT + "/" + file_path + file_name_400, quality=88)
        Thumbnail.objects.create(
            original_image=self,
            height=400,
            width=400,
            thumbnail=file_path + file_name_400,
            valid_until=self.valid_until
        )


class Thumbnail(BaseModelMixin):
    original_image = models.ForeignKey(Image, on_delete=models.CASCADE)
    height = models.IntegerField(default=100, help_text='minimal height')
    width = models.IntegerField(default=100, help_text='minimal width')
    thumbnail = models.ImageField(upload_to=thumbnail_path, blank=True)
    valid_until = models.DateTimeField()


class TierName(BaseModelMixin):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Tier(BaseModelMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.ForeignKey(TierName, on_delete=models.CASCADE)

    def __str__(self):
        return self.name.name
