# Generated by Django 5.0.7 on 2024-08-19 23:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cow_annotator_ui', '0002_annotation_image_delete_annotations'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Image',
            new_name='Photo',
        ),
    ]
