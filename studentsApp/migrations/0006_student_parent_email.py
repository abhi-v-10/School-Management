# Generated manually to add parent_email field
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('studentsApp', '0005_alter_student_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='parent_email',
            field=models.EmailField(null=True, blank=True, max_length=254, help_text="Parent's email for auto-linking if parent registers later"),
        ),
    ]
