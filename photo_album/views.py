from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import generics, views
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Photo
from .permissions import AuthorPermission
from .serializers import (
    UpdatePhotoSerializer,
    PhotoSerializer,
    ListCreatePhotoSerializer,
    VideoSerializer
)


class VideoView(views.APIView):
    """ Generate video
    """
    @extend_schema(
        parameters=[
            OpenApiParameter(
                'personal',
                OpenApiTypes.STR,
                OpenApiParameter.PATH,
                enum=['all', 'me']
            )
        ],
        responses={
            200: OpenApiResponse(response=VideoSerializer,
                                 description='Video url'),
            404: OpenApiResponse(description='Photos not found')
        }
    )
    def get(self, request, personal='all'):
        """ Return generated video
        """
        if personal == 'me':
            photos = Photo.top_photos(request.user)
        elif personal == 'all':
            photos = Photo.top_photos()
        else:
            raise NotFound(detail='Photo not found', code=404)

        if len(photos) == 0:
            raise NotFound(detail='Photo not found', code=404)
        video_url = Photo.generate_movie(photos)
        video_absolute_url = request.build_absolute_uri(video_url)
        serializer = VideoSerializer({'video': video_absolute_url})
        return Response(serializer.data)


class RetrieveUpdatePhotoView(generics.RetrieveUpdateAPIView):
    """ Get or update photo by id
    """
    queryset = Photo.objects.all()
    serializer_class = UpdatePhotoSerializer
    permission_classes = [AuthorPermission, ]
    http_method_names = ['get', 'put']

    def retrieve(self, request, pk):
        """ Return photo by pk
        """
        queryset = Photo.objects.filter(author=request.user)
        photo = get_object_or_404(queryset, pk=pk)
        photo.add_view()
        serializer = PhotoSerializer(photo, context={'request': request})
        return Response(serializer.data)


class ListCreatePhotoView(generics.ListCreateAPIView):
    """ Create photo and get user album
    """
    queryset = Photo.objects.all()
    serializer_class = ListCreatePhotoSerializer
    permission_classes = [IsAuthenticated, ]

    def list(self, request):
        """ Return all photos for current user
        """
        queryset = self.get_queryset().filter(author=request.user)
        serializer = PhotoSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
