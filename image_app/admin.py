import os
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from PIL import Image as Img
from ImageRepository.settings import MEDIA_ROOT
from image_app.models import Image, Tier, TierName, ImageData, Thumbnail


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


class ThumbnailInLine(admin.TabularInline):
    model = Thumbnail
    readonly_fields = ("thumbnail",)
    extra = 0


@admin.register(ImageData)
class ImageDataAdmin(ModelAdmin):
    list_display = [
        "uuid",
        "title",
        "created_at",
    ]
    search_fields = [
        "uuid",
        "title",
    ]
    list_filter = [
        "created_at"
    ]
    inlines = [ImageInline]


@admin.register(Image)
class ImageAdmin(ModelAdmin):
    list_display = [
        "image_data",
        "image",
        "valid_until",
    ]
    list_filter = [
        "valid_until"
    ]
    inlines = [ThumbnailInLine]


@admin.register(Thumbnail)
class ThumbnailAdmin(ModelAdmin):
    list_display = [
        "original_image",
        "height",
        "width",
        "thumbnail",
        "valid_until"
    ]
    readonly_fields = ("thumbnail",)

    def save_model(self, request, obj, form, change):
        original_image = obj.original_image
        original_image_data = original_image.image_data

        file_name = f'{obj.width}_{obj.height}_{original_image.image.name.split("/")[-1]}'
        file_path = f"{original_image_data.user.id}/{original_image_data.uuid}/thumbnails/"

        if not os.path.exists(MEDIA_ROOT + "/" + file_path):
            os.mkdir(MEDIA_ROOT + "/" + file_path)

        if not os.path.exists(MEDIA_ROOT + "/" + file_path + file_name):
            image = Img.open(MEDIA_ROOT + "/" + original_image.image.name)
            image.thumbnail((obj.width, obj.height))
            image.save(MEDIA_ROOT + "/" + file_path + file_name, quality=88)
            obj.thumbnail = file_path + file_name

        super().save_model(request, obj, form, change)


@admin.register(Tier)
class TierAdmin(ModelAdmin):
    list_display = [
        "user",
        "name",
    ]


@admin.register(TierName)
class TierAdmin(ModelAdmin):
    list_display = [
        "name",
    ]
