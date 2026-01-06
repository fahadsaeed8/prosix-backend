# Generated manually - adds price and sku fields to Customizer

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_management_app', '0033_add_subcategory_have_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='customizer',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.00, help_text='Price of the customizer', max_digits=10),
        ),
        migrations.AddField(
            model_name='customizer',
            name='sku',
            field=models.CharField(blank=True, help_text='Stock Keeping Unit', max_length=100, null=True, unique=True),
        ),
    ]

