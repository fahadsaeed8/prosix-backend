# Generated manually - changes Customizer category from CharField to ForeignKey

from django.db import migrations, models
import django.db.models.deletion


def migrate_category_data(apps, schema_editor):
    """
    Migrate existing category string values to Category ForeignKey.
    Since we can't reliably map string values to Category IDs, we'll set them to NULL
    and let the user update them manually, or we can try to find matching categories.
    """
    Customizer = apps.get_model('product_management_app', 'Customizer')
    Category = apps.get_model('website_management_app', 'Category')
    
    # Try to map string category values to Category objects
    category_mapping = {
        'jerseys': 'jerseys',
        'shorts': 'shorts',
        'hoodies': 'hoodies',
        'pants': 'pants',
        'jacket': 'jacket',
        'accessories': 'accessories',
    }
    
    for customizer in Customizer.objects.all():
        if customizer.category:
            # Try to find a matching Category by name (case-insensitive)
            category_name = customizer.category.lower()
            try:
                # Try exact match first
                category = Category.objects.filter(category_name__iexact=category_name).first()
                if not category:
                    # Try partial match
                    category = Category.objects.filter(category_name__icontains=category_name).first()
                
                if category:
                    customizer.category_id = category.id
                    customizer.save(update_fields=['category_id'])
                else:
                    # No match found, set to NULL
                    customizer.category_id = None
                    customizer.save(update_fields=['category_id'])
            except Exception as e:
                # If any error, set to NULL
                customizer.category_id = None
                customizer.save(update_fields=['category_id'])


def reverse_migrate_category_data(apps, schema_editor):
    """
    Reverse migration - convert Category ForeignKey back to string
    """
    Customizer = apps.get_model('product_management_app', 'Customizer')
    
    for customizer in Customizer.objects.all():
        if customizer.category:
            # Use category_name as the string value
            customizer.category = customizer.category.category_name.lower()
            customizer.save(update_fields=['category'])


class Migration(migrations.Migration):

    dependencies = [
        ('product_management_app', '0034_add_customizer_price_sku'),
        ('website_management_app', '0019_category_password_category_show_in'),
    ]

    operations = [
        # Add new ForeignKey field (nullable initially)
        migrations.AddField(
            model_name='customizer',
            name='category_new',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='customizers_category',
                to='website_management_app.category'
            ),
        ),
        # Migrate data
        migrations.RunPython(migrate_category_data, reverse_migrate_category_data),
        # Remove old CharField
        migrations.RemoveField(
            model_name='customizer',
            name='category',
        ),
        # Rename new field to category
        migrations.RenameField(
            model_name='customizer',
            old_name='category_new',
            new_name='category',
        ),
        # Make it non-nullable
        migrations.AlterField(
            model_name='customizer',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='customizers_category',
                to='website_management_app.category'
            ),
        ),
    ]

