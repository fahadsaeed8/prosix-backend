# Generated manually on 2026-01-02

from django.db import migrations, models
import django.db.models.deletion


def rename_description_to_size_if_exists(apps, schema_editor):
    """Rename description to size if description field exists, otherwise just add size"""
    Shirt = apps.get_model('product_management_app', 'Shirt')
    db_table = Shirt._meta.db_table
    
    with schema_editor.connection.cursor() as cursor:
        # Check if description column exists
        cursor.execute(f"PRAGMA table_info({db_table})")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        if 'description' in columns and 'size' not in columns:
            # For SQLite 3.25.0+, use RENAME COLUMN
            try:
                cursor.execute(f"ALTER TABLE {db_table} RENAME COLUMN description TO size")
            except Exception:
                # Fallback for older SQLite: create new table, copy data, drop old
                # This is complex, so we'll use a simpler approach
                # Just add size and copy data from description
                cursor.execute(f"ALTER TABLE {db_table} ADD COLUMN size TEXT")
                cursor.execute(f"UPDATE {db_table} SET size = description")
                # Note: We can't easily drop description in SQLite without recreating table
                # So we'll leave both columns for now
        elif 'size' not in columns:
            # Add size field if it doesn't exist
            cursor.execute(f"ALTER TABLE {db_table} ADD COLUMN size TEXT")


def reverse_rename_size_to_description(apps, schema_editor):
    """Reverse: rename size back to description if needed"""
    Shirt = apps.get_model('product_management_app', 'Shirt')
    db_table = Shirt._meta.db_table
    
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f"PRAGMA table_info({db_table})")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        if 'size' in columns and 'description' not in columns:
            try:
                cursor.execute(f"ALTER TABLE {db_table} RENAME COLUMN size TO description")
            except Exception:
                # Fallback: add description and copy data
                cursor.execute(f"ALTER TABLE {db_table} ADD COLUMN description TEXT")
                cursor.execute(f"UPDATE {db_table} SET description = size")


class Migration(migrations.Migration):

    dependencies = [
        ('product_management_app', '0023_change_draft_to_customizer'),
    ]

    operations = [
        # Create MainShirtImage model
        migrations.CreateModel(
            name='MainShirtImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(help_text='Main shirt image', upload_to='shirts/main_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('shirt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='main_images', to='product_management_app.shirt')),
            ],
            options={
                'verbose_name': 'Main Shirt Image',
                'verbose_name_plural': 'Main Shirt Images',
                'ordering': ['created_at'],
            },
        ),
        # Rename name to title
        migrations.RenameField(
            model_name='shirt',
            old_name='name',
            new_name='title',
        ),
        # Conditionally rename description to size or add size field
        # Use SeparateDatabaseAndState to handle database and model state separately
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    rename_description_to_size_if_exists,
                    reverse_rename_size_to_description,
                ),
            ],
            state_operations=[
                # For state: Add size field (will work whether description exists or not)
                # If description exists in some migration paths, the rename in DB will handle it
                # If description doesn't exist, the DB operation will just add size
                migrations.AddField(
                    model_name='shirt',
                    name='size',
                    field=models.TextField(blank=True, help_text='Size of the shirt', null=True),
                ),
            ],
        ),
        # Add model boolean field
        migrations.AddField(
            model_name='shirt',
            name='model',
            field=models.BooleanField(default=False, help_text='Model flag'),
        ),
        # Remove white image fields
        migrations.RemoveField(
            model_name='shirt',
            name='white_front',
        ),
        migrations.RemoveField(
            model_name='shirt',
            name='white_back',
        ),
        migrations.RemoveField(
            model_name='shirt',
            name='white_left',
        ),
        migrations.RemoveField(
            model_name='shirt',
            name='white_right',
        ),
        # Remove black image fields
        migrations.RemoveField(
            model_name='shirt',
            name='black_front',
        ),
        migrations.RemoveField(
            model_name='shirt',
            name='black_back',
        ),
        migrations.RemoveField(
            model_name='shirt',
            name='black_left',
        ),
        migrations.RemoveField(
            model_name='shirt',
            name='black_right',
        ),
        # Remove svg image fields
        migrations.RemoveField(
            model_name='shirt',
            name='svg_front',
        ),
        migrations.RemoveField(
            model_name='shirt',
            name='svg_back',
        ),
        migrations.RemoveField(
            model_name='shirt',
            name='svg_left',
        ),
        migrations.RemoveField(
            model_name='shirt',
            name='svg_right',
        ),
        # Change sub_category ForeignKey from ShirtSubCategory to SubCategory
        migrations.AlterField(
            model_name='shirt',
            name='sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shirts_subcategory', to='product_management_app.subcategory'),
        ),
    ]

