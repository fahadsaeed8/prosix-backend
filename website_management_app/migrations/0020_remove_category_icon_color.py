# Generated manually - removes icon and color fields from Category

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website_management_app', '0020_remove_category_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='icon',
        ),
        migrations.RemoveField(
            model_name='category',
            name='color',
        ),
    ]

