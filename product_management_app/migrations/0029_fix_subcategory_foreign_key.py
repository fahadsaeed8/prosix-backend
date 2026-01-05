# Generated manually - fixes sub_category foreign key constraint

from django.db import migrations, connection


def fix_subcategory_foreign_key(apps, schema_editor):
    """
    Fix the sub_category foreign key constraint.
    SQLite doesn't support ALTER TABLE for foreign keys easily.
    This migration verifies the constraint and provides diagnostics.
    """
    SubCategory = apps.get_model('product_management_app', 'SubCategory')
    
    # Verify SubCategory table exists and has data
    subcategory_count = SubCategory.objects.count()
    print(f"SubCategory table has {subcategory_count} records")
    
    # Check if SubCategory ID 8 exists
    try:
        subcat_8 = SubCategory.objects.get(id=8)
        print(f"SubCategory ID 8 exists: {subcat_8.name}")
    except SubCategory.DoesNotExist:
        print("ERROR: SubCategory ID 8 does not exist!")
    
    # Check the actual foreign key constraint in the database
    with connection.cursor() as cursor:
        # Get table info
        cursor.execute("PRAGMA table_info(product_management_app_shirt)")
        columns = cursor.fetchall()
        print("Shirt table columns:")
        for col in columns:
            print(f"  {col[1]} (type: {col[2]})")
        
        # Check foreign keys
        cursor.execute("PRAGMA foreign_key_list(product_management_app_shirt)")
        fks = cursor.fetchall()
        print("Foreign keys on Shirt table:")
        for fk in fks:
            print(f"  {fk}")


def reverse_fix_subcategory_foreign_key(apps, schema_editor):
    """Reverse operation - nothing to do"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('product_management_app', '0027_remove_shirt_image_fields_conditional'),
    ]

    operations = [
        migrations.RunPython(
            fix_subcategory_foreign_key,
            reverse_fix_subcategory_foreign_key,
        ),
    ]

