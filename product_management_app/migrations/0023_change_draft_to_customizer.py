# Generated manually on 2026-01-02

from django.db import migrations, models
import django.db.models.deletion


def delete_existing_drafts(apps, schema_editor):
    """Delete existing ShirtDraft records since we're changing the relationship"""
    ShirtDraft = apps.get_model('product_management_app', 'ShirtDraft')
    ShirtDraft.objects.all().delete()


def reverse_delete_drafts(apps, schema_editor):
    """Reverse operation - nothing to do"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('product_management_app', '0022_subcategory'),
    ]

    operations = [
        # Delete existing drafts since we're changing from shirt to customizer
        migrations.RunPython(delete_existing_drafts, reverse_delete_drafts),
        migrations.RemoveField(
            model_name='shirtdraft',
            name='shirt',
        ),
        migrations.AddField(
            model_name='shirtdraft',
            name='customizer',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='draft',
                to='product_management_app.customizer'
            ),
        ),
    ]

