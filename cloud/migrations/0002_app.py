# Generated by Django 2.1.7 on 2019-03-13 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloud', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='App',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('instanceId', models.CharField(max_length=100)),
                ('appName', models.CharField(max_length=100)),
                ('gitLink', models.CharField(max_length=100)),
                ('branch', models.CharField(max_length=100)),
                ('runCmd', models.CharField(max_length=100)),
                ('appLink', models.CharField(max_length=100)),
            ],
        ),
    ]