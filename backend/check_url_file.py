import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pricecube.settings')
django.setup()

import inspect

import pricecube.core.urls as u
print('urls file:', u.__file__)
print('cached:', inspect.getfile(u))
