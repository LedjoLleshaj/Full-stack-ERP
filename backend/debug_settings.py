#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/ledjo/Desktop/selita-fish/backend')

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

print("=== JWT Cookie Settings ===")
print(f"AUTH_COOKIE: {settings.SIMPLE_JWT.get('AUTH_COOKIE')}")
print(f"REFRESH_COOKIE: {settings.SIMPLE_JWT.get('REFRESH_COOKIE')}")
print(f"AUTH_COOKIE_SECURE: {settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE')}")
print(f"AUTH_COOKIE_HTTP_ONLY: {settings.SIMPLE_JWT.get('AUTH_COOKIE_HTTP_ONLY')}")
print(f"AUTH_COOKIE_PATH: {settings.SIMPLE_JWT.get('AUTH_COOKIE_PATH')}")
print(f"AUTH_COOKIE_SAMESITE: {settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE')}")
print(f"ACCESS_TOKEN_LIFETIME: {settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME')}")
print(f"REFRESH_TOKEN_LIFETIME: {settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME')}")
