# Generated manually - changes Customizer category from CharField to ForeignKey

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product_management_app', '0034_add_customizer_price_sku'),
        ('website_management_app', '0019_category_password_category_show_in'),
    ]

    operations = [
        # Add new ForeignKey field (nullable for existing records, you can update them later)
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
    ]

