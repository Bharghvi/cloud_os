# Generated by Django 2.1.7 on 2019-04-13 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloud', '0012_instance_instancename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instance',
            name='instanceName',
            field=models.CharField(default='test-webd', max_length=100),
            preserve_default=False,
        ),
    ]