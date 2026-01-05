# Generated manually - adds have_password boolean field to SubCategory

from django.db import migrations, models


def populate_have_password(apps, schema_editor):
    """Populate have_password field for existing SubCategory records"""
    SubCategory = apps.get_model('product_management_app', 'SubCategory')
    for subcategory in SubCategory.objects.all():
        subcategory.have_password = bool(subcategory.password and subcategory.password.strip())
        subcategory.save(update_fields=['have_password'])


def reverse_populate_have_password(apps, schema_editor):
    """Reverse operation - nothing to do"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('product_management_app', '0032_drop_customizer_model_type_sport'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategory',
            name='have_password',
            field=models.BooleanField(default=False, help_text='True if password is set'),
        ),
        migrations.RunPython(
            populate_have_password,
            reverse_populate_have_password,
        ),
    ]

