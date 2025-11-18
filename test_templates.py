#!/usr/bin/env python
"""
Quick test script to verify navbar and sidebar templates can be loaded
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmm_web_backend.settings.local')
django.setup()

from django.template.loader import get_template
from django.template import TemplateDoesNotExist

def test_template_exists(template_name):
    """Test if a template exists and can be loaded"""
    try:
        template = get_template(template_name)
        print(f"✅ {template_name} - OK (found at {template.origin.name})")
        return True
    except TemplateDoesNotExist:
        print(f"❌ {template_name} - NOT FOUND")
        return False

if __name__ == "__main__":
    print("Testing template implementation...\n")

    templates_to_test = [
        'base.html',
        'navbar.html',
        'sidebar.html',
        'dashboard/dashboard.html',
    ]

    results = []
    for template_name in templates_to_test:
        results.append(test_template_exists(template_name))

    print("\n" + "="*50)
    if all(results):
        print("✅ All templates found successfully!")
    else:
        print("❌ Some templates are missing")
    print("="*50)

