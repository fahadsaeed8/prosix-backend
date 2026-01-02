from django.db import migrations
import json

def fix_sub_category_json(apps, schema_editor):
    Customizer = apps.get_model('product_management_app', 'Customizer')
    for obj in Customizer.objects.all():
        current_value = obj.sub_category
        if current_value is None:
            continue
        # If it's already a list, assume it's valid JSON for JSONField
        if isinstance(current_value, list):
            continue
        new_value = None
        if isinstance(current_value, str):
            s = current_value.strip()
            # Try to detect a JSON-encoded list
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    new_value = parsed
                else:
                    new_value = [str(parsed)]
            except Exception:
                # Not JSON; wrap the string in a list
                new_value = [s]
        else:
            # Fallback: coerce to string and wrap in a list
            new_value = [str(current_value)]
        if new_value is not None:
            obj.sub_category = new_value
            obj.save(update_fields=['sub_category'])

class Migration(migrations.Migration):
    dependencies = [
        ('product_management_app', '0020_merge_20260102_1442'),
    ]

    operations = [
        migrations.RunPython(fix_sub_category_json, reverse_code=migrations.RunPython.noop),
    ]


