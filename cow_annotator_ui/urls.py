from django.urls import path
from django.conf.urls.static import static
from django.conf import settings


from . import views

urlpatterns = [
    path("", views.login, name="login"),
    path("<int:page>/", views.index, name="index"),
    path("images/<int:page>/", views.images, name="images"),
    path("send-annotations/", views.send_annotations, name="send_annotations"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)