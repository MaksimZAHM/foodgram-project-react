# Generated by Django 3.2.12 on 2022-07-30 13:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_amount_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='is_favorited',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='is_in_shopping_cart',
        ),
        migrations.AlterField(
            model_name='amount',
            name='amount',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0.01, 'слишком малое значение')], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'слишком малое значение')], verbose_name='Время приготовления'),
        ),
    ]
