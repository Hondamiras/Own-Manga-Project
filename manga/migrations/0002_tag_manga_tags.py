# Generated by Django 5.1.4 on 2025-05-20 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manga', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='manga',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='mangas', to='manga.tag'),
        ),
    ]
