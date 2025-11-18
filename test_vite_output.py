#!/usr/bin/env python
"""Test script to verify Vite template tag output"""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmm_web_backend.settings.local')
django.setup()

from django.template import Template, Context
from vite.templatetags.vite import enable_vite
from vite import get_config

print("=" * 60)
print("VITE CONFIGURATION TEST")
print("=" * 60)

try:
    vite_dev_mode = get_config('VITE_DEV_MODE')
    print(f"VITE_DEV_MODE: {vite_dev_mode}")
    print(f"VITE_MANIFEST_PATH: {get_config('VITE_MANIFEST_PATH')}")
    print()

    print("Template context from enable_vite():")
    result = enable_vite()
    for key, value in result.items():
        print(f"  {key}: {value}")
    print()

    # Test rendering the actual template
    template_code = """{% load vite %}{% enable_vite %}"""
    template = Template(template_code)
    rendered = template.render(Context({}))

    print("Rendered HTML output:")
    print("-" * 60)
    print(rendered)
    print("-" * 60)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback

    traceback.print_exc()
