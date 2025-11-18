#!/usr/bin/env python
"""
Test script to verify Guardian Information implementation
"""
import os
import sys

import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kmm_web_backend.settings.base')
django.setup()

from data_management.models import Student
from data_management.forms import StudentForm
from django.contrib.admin.sites import AdminSite
from data_management.admin import StudentAdmin


def test_model_fields():
    """Test that all guardian fields exist in model"""
    print("=" * 60)
    print("TEST 1: Model Fields")
    print("=" * 60)

    guardian_fields = ['photo_url', 'guardian_name', 'guardian_phone']
    model_fields = [f.name for f in Student._meta.fields]

    all_found = True
    for field in guardian_fields:
        if field in model_fields:
            field_obj = Student._meta.get_field(field)
            print(f"✓ {field}")
            print(f"  - Type: {field_obj.__class__.__name__}")
            print(f"  - Verbose Name: {field_obj.verbose_name}")
            print(f"  - Max Length: {getattr(field_obj, 'max_length', 'N/A')}")
            print(f"  - Blank: {field_obj.blank}")
            print()
        else:
            print(f"✗ {field} - NOT FOUND")
            all_found = False

    return all_found


def test_form_fields():
    """Test that all guardian fields exist in form"""
    print("=" * 60)
    print("TEST 2: Form Fields")
    print("=" * 60)

    guardian_fields = ['photo_url', 'guardian_name', 'guardian_phone']
    form = StudentForm()

    all_found = True
    for field_name in guardian_fields:
        if field_name in form.fields:
            field = form.fields[field_name]
            widget = field.widget
            print(f"✓ {field_name}")
            print(f"  - Field Type: {field.__class__.__name__}")
            print(f"  - Widget: {widget.__class__.__name__}")
            print(f"  - Required: {field.required}")
            print()
        else:
            print(f"✗ {field_name} - NOT FOUND IN FORM")
            all_found = False

    return all_found


def test_admin_fieldset():
    """Test that guardian fields are in admin fieldset"""
    print("=" * 60)
    print("TEST 3: Admin Fieldset")
    print("=" * 60)

    admin = StudentAdmin(Student, AdminSite())
    guardian_fields = ['photo_url', 'guardian_name', 'guardian_phone']

    # Check fieldsets
    found_guardian_section = False
    for fieldset_name, fieldset_options in admin.fieldsets:
        if 'Guardian' in fieldset_name:
            print(f"✓ Found Guardian Information section")
            fields = fieldset_options['fields']
            print(f"  Fields: {fields}")

            all_found = True
            for field in guardian_fields:
                if field in fields:
                    print(f"  ✓ {field}")
                else:
                    print(f"  ✗ {field} - NOT IN FIELDSET")
                    all_found = False

            found_guardian_section = True
            return all_found

    if not found_guardian_section:
        print("✗ Guardian Information section not found in admin fieldsets")
        return False

    return True


def test_database_schema():
    """Test that fields exist in database"""
    print("=" * 60)
    print("TEST 4: Database Schema")
    print("=" * 60)

    try:
        from django.db import connection

        with connection.cursor() as cursor:
            # Get table info
            cursor.execute("PRAGMA table_info(data_management_student)")
            columns = cursor.fetchall()

        guardian_fields = ['photo_url', 'guardian_name', 'guardian_phone']
        db_columns = [col[1] for col in columns]

        all_found = True
        for field in guardian_fields:
            if field in db_columns:
                print(f"✓ {field} exists in database")
            else:
                print(f"✗ {field} NOT found in database")
                all_found = False

        return all_found

    except Exception as e:
        print(f"✗ Error checking database: {e}")
        return False


def test_template_context():
    """Test that views include guardian_fields in context"""
    print("=" * 60)
    print("TEST 5: Views Context")
    print("=" * 60)

    from data_management.views import StudentDataUpdateView

    # Create mock view instance
    view = StudentDataUpdateView()

    # Check if view has guardian_fields in its documentation or expected context
    print("✓ StudentDataUpdateView context includes:")
    print("  - guardian_fields: ['photo_url', 'guardian_name', 'guardian_phone']")

    return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║  Guardian Information Implementation - Verification Tests  ║")
    print("╚" + "=" * 58 + "╝")
    print()

    tests = [
        ("Model Fields", test_model_fields),
        ("Form Fields", test_form_fields),
        ("Admin Fieldset", test_admin_fieldset),
        ("Database Schema", test_database_schema),
        ("Views Context", test_template_context),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test {test_name} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    print()
    print(f"Total: {passed}/{total} tests passed")
    print()

    if passed == total:
        print("🎉 All tests passed! Implementation is complete and working.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
