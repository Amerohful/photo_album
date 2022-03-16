from django.urls import path

from .views import ListCreatePhotoView, RetrieveUpdatePhotoView, VideoView

app_name = 'photo'
urlpatterns = [
    path('', ListCreatePhotoView.as_view(), name='list_create_photo'),
    path('<int:pk>', RetrieveUpdatePhotoView.as_view(), name='retrieve_update_photo'),
    path('get_video/<personal>/', VideoView.as_view(), name='get_video'),
]
