# Generated by Django 5.0.1 on 2024-02-02 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transiction', '0002_transaction_is_bankcrupt_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankCrupt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_bankcrupt', models.BooleanField(blank=True, default=False, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='is_bankcrupt',
        ),
    ]
