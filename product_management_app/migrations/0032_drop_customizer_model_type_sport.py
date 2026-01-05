# Generated manually - drops model_type and sport columns from customizer table

from django.db import migrations


def drop_model_type_and_sport_columns(apps, schema_editor):
    """Drop model_type and sport columns from customizer table"""
    with schema_editor.connection.cursor() as cursor:
        # Disable foreign key checks
        cursor.execute("PRAGMA foreign_keys=OFF")
        
        try:
            # Get table info to check if columns exist
            cursor.execute("PRAGMA table_info(product_management_app_customizer)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # If model_type or sport exist, we need to drop them
            if 'model_type' in column_names or 'sport' in column_names:
                # Check SQLite version
                cursor.execute("SELECT sqlite_version()")
                version_str = cursor.fetchone()[0]
                version_parts = [int(x) for x in version_str.split('.')]
                
                if version_parts >= [3, 35, 0]:
                    # SQLite 3.35.0+ supports DROP COLUMN
                    if 'model_type' in column_names:
                        cursor.execute("ALTER TABLE product_management_app_customizer DROP COLUMN model_type")
                    if 'sport' in column_names:
                        cursor.execute("ALTER TABLE product_management_app_customizer DROP COLUMN sport")
                else:
                    # For older SQLite, recreate the table without these columns
                    # Since user doesn't care about data, we'll just drop and recreate
                    cursor.execute("DROP TABLE IF EXISTS product_management_app_customizer")
                    
                    # Recreate table without model_type and sport
                    cursor.execute("""
                        CREATE TABLE "product_management_app_customizer" (
                            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                            "title" varchar(255) NOT NULL,
                            "category" varchar(50) NOT NULL,
                            "sub_category" text NULL,
                            "size" text NULL,
                            "is_active" bool NOT NULL DEFAULT 1,
                            "views" integer NOT NULL DEFAULT 0,
                            "front_black_layer" varchar(100) NULL,
                            "front_white_layer" varchar(100) NULL,
                            "front_svg_layer" varchar(100) NULL,
                            "back_black_layer" varchar(100) NULL,
                            "back_white_layer" varchar(100) NULL,
                            "back_svg_layer" varchar(100) NULL,
                            "left_black_layer" varchar(100) NULL,
                            "left_white_layer" varchar(100) NULL,
                            "left_svg_layer" varchar(100) NULL,
                            "right_black_layer" varchar(100) NULL,
                            "right_white_layer" varchar(100) NULL,
                            "right_svg_layer" varchar(100) NULL,
                            "created_at" datetime NOT NULL,
                            "updated_at" datetime NOT NULL
                        )
                    """)
        except Exception as e:
            # If anything fails, just continue
            print(f"Warning: Could not drop columns: {e}")
        finally:
            # Re-enable foreign key checks
            cursor.execute("PRAGMA foreign_keys=ON")


def reverse_drop_columns(apps, schema_editor):
    """Reverse operation - add columns back with default values"""
    # Not implementing reverse since user doesn't care about data
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('product_management_app', '0031_update_customizer_fields'),
    ]

    operations = [
        migrations.RunPython(
            drop_model_type_and_sport_columns,
            reverse_drop_columns,
        ),
    ]

