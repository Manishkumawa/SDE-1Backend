from django.shortcuts import render
import csv

from django.http import JsonResponse
from .models import ImageProcessingRequest,ProductImage

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import os
import tempfile

from .tasks import process_image
@csrf_exempt
def upload_csv(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]

        
        processing_request = ImageProcessingRequest.objects.create(status="pending")

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        errors = []
        processed_records = 0

        try:
            with open(temp_file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader, None)  
                
                if not header or len(header) < 3:
                    return JsonResponse({"error": "Invalid CSV format. Expected columns: Serial Number, Product Name, Input Images"}, status=400)

                for line_number, row in enumerate(reader, start=2):  
                    if len(row) != 3:
                        errors.append(f"Row {line_number}: Incorrect number of columns.")
                        continue
                    
                    serial_number, product_name, input_images = row

                   
                    try:
                        serial_number = int(serial_number)
                        if serial_number <= 0:
                            raise ValueError("Serial number must be positive.")
                    except ValueError:
                        errors.append(f"Row {line_number}: Invalid serial number '{serial_number}', must be a positive integer.")
                        continue

                   
                    if not product_name.strip():
                        errors.append(f"Row {line_number}: Product name cannot be empty.")
                        continue

                    # Validate input_images (should be a non-empty string)
                    if not input_images.strip():
                        errors.append(f"Row {line_number}: Input image URL(s) cannot be empty.")
                        continue

                    # Save valid row to the database
                    ProductImage.objects.create(
                        request=processing_request,
                        serial_number=serial_number,
                        product_name=product_name.strip(),
                        input_image_urls=input_images.strip(),
                    )
                    process_image.delay(str(processing_request.request_id))
                    processed_records += 1

        finally:
            os.remove(temp_file_path)

        if errors:
            return JsonResponse({"error": "CSV validation failed", "details": errors}, status=400)

        return JsonResponse({"request_id": str(processing_request.request_id), "processed_records": processed_records})

    return JsonResponse({"error": "Invalid request"}, status=400)



def check_status(request,request_id):

    processing_request = get_object_or_404(ImageProcessingRequest,request_id = request_id)

    return JsonResponse({"request_id":str(processing_request.request_id),"status":processing_request.status})


