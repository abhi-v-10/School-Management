from django.db import migrations, models
import resourcesApp.models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classesApp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('file', models.FileField(upload_to=resourcesApp.models.resource_upload_path)),
                ('resource_type', models.CharField(choices=[('document', 'Document'), ('presentation', 'Presentation'), ('image', 'Image'), ('other', 'Other')], default='document', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('class_room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='classesApp.classroom')),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resources', to='classesApp.subjects')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_resources', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(default=5)),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='resourcesApp.resource')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resource_ratings', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterUniqueTogether(name='resourcerating', unique_together={('resource', 'student')}),
    ]
