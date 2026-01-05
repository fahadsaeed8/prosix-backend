# Generated manually - drops and recreates Shirt table with correct foreign key

from django.db import migrations


def recreate_shirt_table(apps, schema_editor):
    """Drop and recreate Shirt table with correct foreign key - deletes all data"""
    with schema_editor.connection.cursor() as cursor:
        # Disable foreign key checks
        cursor.execute("PRAGMA foreign_keys=OFF")
        
        try:
            # Drop all tables that reference Shirt first
            cursor.execute("DROP TABLE IF EXISTS product_management_app_favoriteshirt")
            cursor.execute("DROP TABLE IF EXISTS product_management_app_usershirt")
            cursor.execute("DROP TABLE IF EXISTS product_management_app_mainshirtimage")
            cursor.execute("DROP TABLE IF EXISTS product_management_app_shirtimage")
            
            # Drop the Shirt table
            cursor.execute("DROP TABLE IF EXISTS product_management_app_shirt")
            
            # Create new Shirt table with correct foreign key pointing to SubCategory
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
            
            # Recreate MainShirtImage table
            cursor.execute("""
                CREATE TABLE "product_management_app_mainshirtimage" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "image" varchar(100) NOT NULL,
                    "created_at" datetime NOT NULL,
                    "updated_at" datetime NOT NULL,
                    "shirt_id" bigint NOT NULL REFERENCES "product_management_app_shirt" ("id") DEFERRABLE INITIALLY DEFERRED
                )
            """)
            cursor.execute("CREATE INDEX product_management_app_mainshirtimage_shirt_id_idx ON product_management_app_mainshirtimage(shirt_id)")
            
            # Recreate ShirtImage table
            cursor.execute("""
                CREATE TABLE "product_management_app_shirtimage" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "image" varchar(100) NOT NULL,
                    "created_at" datetime NOT NULL,
                    "updated_at" datetime NOT NULL,
                    "shirt_id" bigint NOT NULL REFERENCES "product_management_app_shirt" ("id") DEFERRABLE INITIALLY DEFERRED
                )
            """)
            cursor.execute("CREATE INDEX product_management_app_shirtimage_shirt_id_idx ON product_management_app_shirtimage(shirt_id)")
            
            # Recreate UserShirt table
            cursor.execute("""
                CREATE TABLE "product_management_app_usershirt" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "colors" text NOT NULL,
                    "created_at" datetime NOT NULL,
                    "updated_at" datetime NOT NULL,
                    "shirt_id" bigint NOT NULL REFERENCES "product_management_app_shirt" ("id") DEFERRABLE INITIALLY DEFERRED,
                    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
                )
            """)
            cursor.execute("CREATE INDEX product_management_app_usershirt_shirt_id_idx ON product_management_app_usershirt(shirt_id)")
            cursor.execute("CREATE INDEX product_management_app_usershirt_user_id_idx ON product_management_app_usershirt(user_id)")
            
            # Recreate FavoriteShirt table
            cursor.execute("""
                CREATE TABLE "product_management_app_favoriteshirt" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "shirt_id" bigint NULL REFERENCES "product_management_app_shirt" ("id") DEFERRABLE INITIALLY DEFERRED,
                    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
                    "user_shirt_id" bigint NULL REFERENCES "product_management_app_usershirt" ("id") DEFERRABLE INITIALLY DEFERRED
                )
            """)
            cursor.execute("CREATE INDEX product_management_app_favoriteshirt_shirt_id_idx ON product_management_app_favoriteshirt(shirt_id)")
            cursor.execute("CREATE INDEX product_management_app_favoriteshirt_user_id_idx ON product_management_app_favoriteshirt(user_id)")
            cursor.execute("CREATE INDEX product_management_app_favoriteshirt_user_shirt_id_idx ON product_management_app_favoriteshirt(user_shirt_id)")
            
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
            recreate_shirt_table,
            reverse_recreate_shirt_table,
        ),
    ]

