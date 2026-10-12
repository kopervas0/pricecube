import django, rest_framework, celery, redis, requests, pandas, openpyxl

print("Django", django.get_version())
print("DRF", rest_framework.VERSION)
print("Celery", celery.__version__)
print("pandas", pandas.__version__)
print("openpyxl", openpyxl.__version__)
