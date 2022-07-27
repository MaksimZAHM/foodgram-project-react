from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import (Amount, Favorite, Ingredient,
                            Recipe, ShoppingCart, Tag)
from recipes.serializers import Base64ImageField
from users.serializers import UserSerializer
from foodgram.settings import (MIN_NAME_LENGTH, MIN_TEXT_LENGTH,
                               MIN_VALUE_COOKING_TIME)


class TagListField(serializers.RelatedField):

    def to_representation(self, obj):
        return {
            'id': obj.id,
            'name': obj.name,
            'color': obj.color,
            'slug': obj.slug
        }

    def to_internal_value(self, data):
        return get_object_or_404(Tag, id=data)


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('name', 'color', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientsAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_name'
    )
    measurement_unit = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_measurement_unit'
    )

    class Meta:
        model = Amount
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def _get_ingredient(self, ingredient_id):
        return get_object_or_404(Ingredient, id=ingredient_id)

    def get_name(self, amount):
        return self._get_ingredient(amount.ingredient.id).name

    def get_measurement_unit(self, amount):
        return self._get_ingredient(amount.ingredient.id).measurement_unit


class RecipesSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientsAmountSerializer(many=True)
    tags = TagsSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_is_in_shopping_cart'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            ).exists()
        return False


class RecipesCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientsAmountSerializer(many=True)
    tags = TagListField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('is_favorited', 'is_in_shopping_cart')

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        amounts = []
        for ingredient in ingredients:
            amount, status = Amount.objects.get_or_create(**ingredient)
            amounts.append(amount)
        recipe.ingredients.set(amounts)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.save()
        amounts = []
        for ingredient in ingredients:
            amount, status = Amount.objects.get_or_create(**ingredient)
            amounts.append(amount)
        instance.ingredients.set(amounts)
        instance.tags.set(tags)
        return instance

    def validate_name(self, name):
        if not name.split()[0].istitle():
            raise serializers.ValidationError(
                'Название должно начинаться с заглавной буквы!'
            )
        elif len(name) < MIN_NAME_LENGTH:
            raise serializers.ValidationError(
                f'Название должно содержать от {MIN_NAME_LENGTH} символов!'
            )
        return name

    def validate_text(self, text):
        if not text.split()[0].istitle():
            raise serializers.ValidationError(
                'Описание должно начинаться с заглавной буквы!'
            )
        elif len(text) < MIN_TEXT_LENGTH:
            raise serializers.ValidationError(
                f'Описание должно содержать от {MIN_TEXT_LENGTH} символов!'
            )
        return text

    def validate_cooking_time(self, data):
        if int(data) < MIN_VALUE_COOKING_TIME:
            raise serializers.ValidationError(
                'время приготовления'
                f'не может быть меньше {MIN_VALUE_COOKING_TIME}')
        return data
