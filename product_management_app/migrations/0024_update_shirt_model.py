# Generated manually on 2026-01-02

from django.db import migrations, models
import django.db.models.deletion


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
        # Rename description to size
        migrations.RenameField(
            model_name='shirt',
            old_name='description',
            new_name='size',
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

