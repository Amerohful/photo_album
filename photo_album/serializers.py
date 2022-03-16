import imghdr
import base64
import uuid
import six

from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Photo


class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):
        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                _, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = f'{file_name}.{file_extension}'

            data = ContentFile(decoded_file, name=complete_file_name)

        return super().to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        extension = 'jpg' if extension == 'jpeg' else extension

        return extension


class PhotoSerializer(serializers.ModelSerializer):
    photo_thumbnail = serializers.SerializerMethodField('get_thumbnail_url')
    photo_webp = serializers.SerializerMethodField('get_webp_url')

    class Meta:
        model = Photo
        fields = ['id', 'name', 'photo', 'photo_thumbnail', 'photo_webp', 'view_counter']
        read_only_fields = ['photo_webp', 'photo_thumbnail', 'view_counter', 'created_at']

    def get_thumbnail_url(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(obj.photo_thumbnail.url)

    def get_webp_url(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(obj.photo_webp.url)


class UpdatePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'
        read_only_fields = ['author', 'photo', 'view_counter', 'created_at']


class ListCreatePhotoSerializer(PhotoSerializer):
    photo = Base64ImageField(allow_empty_file=False)

    def validate_photo(self, value):
        if value.size > settings.IMAGE_SIZE_LIMIT * 1024 * 1024:
            raise ValidationError(f'Max photo size is {settings.IMAGE_SIZE_LIMIT}MB')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        photo = Photo(**validated_data, author=user)
        photo.save()
        return photo


class VideoSerializer(serializers.Serializer):
    video = serializers.CharField()
