# Generated by Django 2.1.1 on 2018-09-29 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Monster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Using an existing name will overwrite that entry. <br>Using a new name will create a new entry<br>', max_length=50, unique=True)),
                ('size', models.CharField(blank=True, max_length=20, null=True)),
                ('type', models.CharField(blank=True, max_length=20, null=True)),
                ('alignment', models.CharField(blank=True, max_length=20, null=True)),
                ('ac', models.IntegerField(blank=True, null=True)),
                ('hp', models.CharField(blank=True, max_length=12, null=True)),
                ('speed', models.TextField(blank=True, null=True)),
                ('str_mod', models.IntegerField(blank=True, null=True)),
                ('dex_mod', models.IntegerField(blank=True, null=True)),
                ('con_mod', models.IntegerField(blank=True, null=True)),
                ('int_mod', models.IntegerField(blank=True, null=True)),
                ('wis_mod', models.IntegerField(blank=True, null=True)),
                ('cha_mod', models.IntegerField(blank=True, null=True)),
                ('saving_throws', models.TextField(blank=True, null=True)),
                ('skills', models.TextField(blank=True, null=True)),
                ('vulnerabilies', models.TextField(blank=True, null=True)),
                ('resistances', models.TextField(blank=True, null=True)),
                ('immunities', models.TextField(blank=True, null=True)),
                ('senses', models.TextField(blank=True, null=True)),
                ('languages', models.TextField(blank=True, null=True)),
                ('cr', models.FloatField(null=True)),
                ('xp', models.IntegerField(null=True)),
                ('traits', models.TextField(blank=True, null=True)),
                ('actions', models.TextField(blank=True, null=True)),
                ('legendary_actions', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
