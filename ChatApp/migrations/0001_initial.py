# Generated by Django 5.0.6 on 2024-05-19 09:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Groups',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=30)),
                ('Limit', models.PositiveIntegerField(default=2)),
                ('Password', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('Role', models.CharField(default='member', max_length=10)),
                ('ReportCount', models.PositiveIntegerField(default=0)),
                ('isOnline', models.BooleanField(default=True)),
                ('Group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ChatApp.groups')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reported_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reported', to='ChatApp.member')),
                ('reported_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='ChatApp.member')),
            ],
            options={
                'unique_together': {('reported_member', 'reported_by')},
            },
        ),
    ]
