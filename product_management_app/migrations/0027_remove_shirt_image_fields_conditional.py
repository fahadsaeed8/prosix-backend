# Generated manually - conditionally removes image fields only if they exist

from django.db import migrations, models


class ConditionalRemoveField(migrations.operations.fields.RemoveField):
    """RemoveField that only removes if the field exists in state, and skips database operation"""
    def state_forwards(self, app_label, state):
        model_state = state.models.get((app_label, self.model_name_lower))
        if model_state and self.name in model_state.fields:
            super().state_forwards(app_label, state)
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # Skip database operation - SQLite doesn't support DROP COLUMN easily
        # and user doesn't care about data. The columns will remain but won't be used.
        pass
    
    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        # Skip reverse operation
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('product_management_app', '0026_merge_0024_merge_20260105_1544_0025_alter_shirt_size'),
    ]

    operations = [
        # Conditionally remove fields from state only if they exist
        # Database operations are skipped since SQLite can't easily drop columns
        ConditionalRemoveField(model_name='shirt', name='black_back'),
        ConditionalRemoveField(model_name='shirt', name='black_front'),
        ConditionalRemoveField(model_name='shirt', name='black_left'),
        ConditionalRemoveField(model_name='shirt', name='black_right'),
        ConditionalRemoveField(model_name='shirt', name='svg_back'),
        ConditionalRemoveField(model_name='shirt', name='svg_front'),
        ConditionalRemoveField(model_name='shirt', name='svg_left'),
        ConditionalRemoveField(model_name='shirt', name='svg_right'),
        ConditionalRemoveField(model_name='shirt', name='white_back'),
        ConditionalRemoveField(model_name='shirt', name='white_front'),
        ConditionalRemoveField(model_name='shirt', name='white_left'),
        ConditionalRemoveField(model_name='shirt', name='white_right'),
        ConditionalRemoveField(model_name='shirt', name='description'),
    ]
