# Generated by Django 5.1.5 on 2025-02-24 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecolution', '0011_alter_pet_pet_level'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='pet',
            name='pet_exp_range',
        ),
        migrations.AddConstraint(
            model_name='pet',
            constraint=models.CheckConstraint(condition=models.Q(('pet_exp__gte', 0), ('pet_exp__lte', 100)), name='pet_exp_range'),
        ),
    ]
