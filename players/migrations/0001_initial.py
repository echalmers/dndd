# Generated by Django 2.1.1 on 2018-09-08 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('ac', models.IntegerField()),
                ('init_mod', models.IntegerField()),
            ],
        ),
    ]
