# Generated manually - updates Customizer model fields
# Renames model_name to title, removes model_type and sport, renames description to size

from django.db import migrations, models


class ConditionalRemoveField(migrations.operations.fields.RemoveField):
    """RemoveField that only removes if the field exists in state"""
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
        ('product_management_app', '0030_verify_subcategory_fk'),
    ]

    operations = [
        # Rename model_name to title
        migrations.RenameField(
            model_name='customizer',
            old_name='model_name',
            new_name='title',
        ),
        # Rename description to size
        migrations.RenameField(
            model_name='customizer',
            old_name='description',
            new_name='size',
        ),
        # Conditionally remove model_type and sport fields
        ConditionalRemoveField(model_name='customizer', name='model_type'),
        ConditionalRemoveField(model_name='customizer', name='sport'),
    ]

