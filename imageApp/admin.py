from django.contrib import admin

# Register your models here.
from .models import ImageProcessingRequest,ProductImage
admin.site.register(ProductImage)
admin.site.register(ImageProcessingRequest)

