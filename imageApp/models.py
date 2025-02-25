from django.db import models
import uuid


class ImageProcessingRequest(models.Model):

    request_id = models.UUIDField(default = uuid.uuid4,unique=True,editable=False,primary_key= True)
    created_at  = models.DateTimeField(auto_now_add= True)

    status = models.CharField(max_length=20 ,choices= [('pending','Pending'),('processing','Processing'),('completed','Completed')])


class ProductImage(models.Model):
    request = models.ForeignKey(ImageProcessingRequest,on_delete=models.CASCADE)

    serial_number = models.IntegerField()
    product_name = models.CharField(max_length=255)
    input_image_urls = models.TextField()
    output_image_urls = models.TextField(blank =True,null=True)
    