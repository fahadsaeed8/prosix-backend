# Generated manually - drops and recreates Shirt table with correct foreign key

from django.db import migrations


def recreate_shirt_table(apps, schema_editor):
    """Drop and recreate Shirt table with correct foreign key - deletes all data"""
    with schema_editor.connection.cursor() as cursor:
        # Disable foreign key checks
        cursor.execute("PRAGMA foreign_keys=OFF")
        
        try:
            # Drop the old table (deletes all data)
            cursor.execute("DROP TABLE IF EXISTS product_management_app_shirt")
            
            # Create new table with correct foreign key pointing to SubCategory
            cursor.execute("""
                CREATE TABLE "product_management_app_shirt" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "title" varchar(255) NOT NULL,
                    "category_id" bigint NOT NULL REFERENCES "website_management_app_category" ("id") DEFERRABLE INITIALLY DEFERRED,
                    "sub_category_id" bigint NULL REFERENCES "product_management_app_subcategory" ("id") DEFERRABLE INITIALLY DEFERRED,
                    "price" decimal NOT NULL DEFAULT 0.00,
                    "sku" varchar(100) NULL UNIQUE,
                    "size" text NULL,
                    "model" bool NOT NULL DEFAULT 0,
                    "created_at" datetime NOT NULL,
                    "updated_at" datetime NOT NULL
                )
            """)
            
            # Recreate indexes
            cursor.execute("CREATE INDEX product_management_app_shirt_category_id_idx ON product_management_app_shirt(category_id)")
            cursor.execute("CREATE INDEX product_management_app_shirt_sub_category_id_idx ON product_management_app_shirt(sub_category_id)")
            
        finally:
            # Re-enable foreign key checks
            cursor.execute("PRAGMA foreign_keys=ON")


def reverse_recreate_shirt_table(apps, schema_editor):
    """Reverse operation - nothing to do"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('product_management_app', '0027_remove_shirt_image_fields_conditional'),
        ('website_management_app', '0019_category_password_category_show_in'),
    ]

    operations = [
        migrations.RunPython(
            recreate_shirt_table_with_correct_fk,
            reverse_recreate_shirt_table,
        ),
    ]

