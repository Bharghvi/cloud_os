# Generated by Django 2.1.7 on 2019-04-03 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cloud', '0004_auto_20190403_1703'),
    ]

    operations = [
        migrations.CreateModel(
            name='SoftDependency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=1)),
                ('dependency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dependency', to='cloud.Software')),
                ('depender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='depender', to='cloud.Software')),
            ],
        ),
    ]
