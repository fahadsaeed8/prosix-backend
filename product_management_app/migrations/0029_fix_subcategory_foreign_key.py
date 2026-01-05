# Generated manually - fixes sub_category foreign key constraint by recreating table

from django.db import migrations, connection


def recreate_shirt_table_with_correct_fk(apps, schema_editor):
    """
    Recreate the Shirt table with the correct foreign key constraint.
    SQLite doesn't support ALTER TABLE to change foreign keys, so we need to recreate the table.
    """
    db = schema_editor.connection.alias
    with schema_editor.connection.cursor() as cursor:
        # Disable foreign key checks temporarily
        cursor.execute("PRAGMA foreign_keys=OFF")
        
        try:
            # Backup existing data (if any)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_management_app_shirt_backup AS 
                SELECT * FROM product_management_app_shirt
            """)
            
            # Get current table structure to preserve data types
            cursor.execute("PRAGMA table_info(product_management_app_shirt)")
            columns_info = cursor.fetchall()
            
            # Drop the old table
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
            cursor.execute("CREATE INDEX IF NOT EXISTS product_management_app_shirt_category_id_idx ON product_management_app_shirt(category_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS product_management_app_shirt_sub_category_id_idx ON product_management_app_shirt(sub_category_id)")
            
            # Restore data from backup, but only if sub_category_id exists in SubCategory table
            SubCategory = apps.get_model('product_management_app', 'SubCategory')
            valid_subcategory_ids = list(SubCategory.objects.values_list('id', flat=True))
            
            cursor.execute("SELECT COUNT(*) FROM product_management_app_shirt_backup")
            backup_count = cursor.fetchone()[0]
            
            if backup_count > 0:
                # Copy data back, but set sub_category_id to NULL if it's invalid
                if valid_subcategory_ids:
                    # Build the IN clause
                    placeholders = ','.join(['?'] * len(valid_subcategory_ids))
                    cursor.execute(f"""
                        INSERT INTO product_management_app_shirt 
                        (id, title, category_id, sub_category_id, price, sku, size, model, created_at, updated_at)
                        SELECT 
                            id, 
                            COALESCE(title, '') as title, 
                            category_id,
                            CASE 
                                WHEN sub_category_id IN ({placeholders}) THEN sub_category_id
                                ELSE NULL
                            END as sub_category_id,
                            COALESCE(price, 0.00) as price,
                            sku,
                            size,
                            COALESCE(model, 0) as model,
                            COALESCE(created_at, datetime('now')) as created_at,
                            COALESCE(updated_at, datetime('now')) as updated_at
                        FROM product_management_app_shirt_backup
                    """, valid_subcategory_ids)
                else:
                    # No valid subcategories, set all to NULL
                    cursor.execute("""
                        INSERT INTO product_management_app_shirt 
                        (id, title, category_id, sub_category_id, price, sku, size, model, created_at, updated_at)
                        SELECT 
                            id, 
                            COALESCE(title, '') as title, 
                            category_id,
                            NULL as sub_category_id,
                            COALESCE(price, 0.00) as price,
                            sku,
                            size,
                            COALESCE(model, 0) as model,
                            COALESCE(created_at, datetime('now')) as created_at,
                            COALESCE(updated_at, datetime('now')) as updated_at
                        FROM product_management_app_shirt_backup
                    """)
            
            # Drop backup table
            cursor.execute("DROP TABLE IF EXISTS product_management_app_shirt_backup")
            
        finally:
            # Re-enable foreign key checks
            cursor.execute("PRAGMA foreign_keys=ON")


def reverse_recreate_shirt_table(apps, schema_editor):
    """Reverse operation - nothing to do since we're just fixing the constraint"""
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

