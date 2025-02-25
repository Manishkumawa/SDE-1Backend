
from celery import shared_task
import requests
from io import BytesIO
from PIL import Image
import os
from .models import ProductImage,ImageProcessingRequest



@shared_task
def process_image(request_id):
    processing_request = ImageProcessingRequest.objects.get(request_id = request_id)

    processing_request.status = "processing"
    processing_request.save()


    for product in ProductImage.objects.filter(request = processing_request):

        input_urls = product.input_image_urls.split(',')
        output_urls = []
        for url in input_urls:
            response = requests.get(url.strip())

            if response.status_code ==200:

                img  =Image.open(BytesIO(response.content))

                output_buffer= BytesIO()
                img.save(output_buffer,format ="JPEG",quality =50)

                output_path = f"processed/{os.path.basename(url.strip())}"

                output_urls.append(f"{output_path}")


        product.output_image_urls = ",".join(output_urls)

        product.save()

    processing_request.status = "completed"
    processing_request.save()

