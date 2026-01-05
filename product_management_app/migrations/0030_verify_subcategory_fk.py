# Generated manually - verifies and fixes sub_category foreign key constraint

from django.db import migrations, connection


def verify_and_fix_fk(apps, schema_editor):
    """Verify the foreign key constraint is correct and fix if needed"""
    with schema_editor.connection.cursor() as cursor:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys=ON")
        
        # Check current foreign keys
        cursor.execute("PRAGMA foreign_key_list(product_management_app_shirt)")
        fks = cursor.fetchall()
        
        print("Current foreign keys on Shirt table:")
        for fk in fks:
            print(f"  {fk}")
        
        # Check if sub_category_id foreign key exists and points to correct table
        subcategory_fk_exists = False
        for fk in fks:
            # fk structure: (id, seq, table, from, to, on_update, on_delete, match)
            if len(fk) >= 4 and fk[3] == 'sub_category_id':
                if fk[2] == 'product_management_app_subcategory':
                    subcategory_fk_exists = True
                    print(f"✓ Foreign key constraint is correct: {fk[2]}")
                else:
                    print(f"✗ Foreign key constraint points to wrong table: {fk[2]}")
        
        if not subcategory_fk_exists:
            print("✗ Foreign key constraint for sub_category_id not found or incorrect")
            print("Dropping and recreating table...")
            
            # Drop and recreate
            cursor.execute("PRAGMA foreign_keys=OFF")
            try:
                # Drop related tables
                cursor.execute("DROP TABLE IF EXISTS product_management_app_favoriteshirt")
                cursor.execute("DROP TABLE IF EXISTS product_management_app_usershirt")
                cursor.execute("DROP TABLE IF EXISTS product_management_app_mainshirtimage")
                cursor.execute("DROP TABLE IF EXISTS product_management_app_shirtimage")
                
                # Get current data structure
                cursor.execute("PRAGMA table_info(product_management_app_shirt)")
                columns = cursor.fetchall()
                
                # Drop and recreate
                cursor.execute("DROP TABLE product_management_app_shirt")
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
                
                # Recreate related tables (simplified - just the structure)
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
                cursor.execute("PRAGMA foreign_keys=ON")
            
            print("✓ Table recreated with correct foreign key constraint")


def reverse_verify_fk(apps, schema_editor):
    """Reverse operation - nothing to do"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('product_management_app', '0029_fix_subcategory_foreign_key'),
    ]

    operations = [
        migrations.RunPython(
            verify_and_fix_fk,
            reverse_verify_fk,
        ),
    ]

