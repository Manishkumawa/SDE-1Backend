from django.urls import path
from .views import upload_csv, check_status


urlpatterns = [
    path("upload", upload_csv, name="upload_csv"),
    path("status/<uuid:request_id>/", check_status, name="check_status"),
]