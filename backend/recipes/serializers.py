from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from users.serializers import CustomUserSerializer
from django.db.models import F

from .models import (
    Tag, Recipe, Ingredient, Favorite, RecipeIngredient, ShoppingList
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ShowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShowRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ShowRecipeFullSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
                  'image', 'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return ShowRecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(recipe=obj,
                                           user=request.user).exists()


class AddRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class AddRecipeSerializer(serializers.ModelSerializer):
    ingredients = AddRecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'image', 'name',
                  'author', 'text', 'cooking_time')

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError('Нужно выбрать минимум 1 ингредиент!')
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise ValidationError('Количество должно быть положительным!')
        ingredients_count = len(ingredients)
        ingredients_set = len(set([i['id'] for i in ingredients]))
        if ingredients_count > ingredients_set:
            raise ValidationError('Ингредиенты не должны повторяться')
        return data

    def validate_cooking_time(self, data):
        if data <= 0:
            raise ValidationError('Время приготовления не должно'
                                  'быть нулем или отрицательным числом')
        return data

    def add_recipe_ingredients(self, ingredients, recipe):
        all_ingredients = []

        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            all_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_id,
                    amount=amount
                )
            )
            # if (RecipeIngredient.objects.
            #         filter(recipe=recipe, ingredient=ingredient_id).exists()):
            #     amount += F('amount')
        RecipeIngredient.objects.bulk_create(all_ingredients)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.ingredients.clear()
        self.add_recipe_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, recipe, validated_data):
        recipe.text = validated_data.get('text', recipe.text)
        recipe.name = validated_data.get('name', recipe.name)
        recipe.cooking_time = validated_data.get('cooking_time',
                                                 recipe.cooking_time)
        recipe.image = validated_data.get('image', recipe.image)
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients.clear()
            self.add_recipe_ingredients(ingredients, recipe)
        if 'tags' in self.initial_data:
            tags_datas = validated_data.pop('tags')
            recipe.tags.set(tags_datas)
        recipe.save()
        return recipe

    def to_representation(self, recipe):
        data = ShowRecipeSerializer(
            recipe, context={'request': self.context.get('request')}).data
        return data


class FavouriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if Favorite.objects.filter(user=user, recipe__id=recipe_id).exists():
            raise ValidationError('Рецепт уже добавлен в избранное')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowRecipeSerializer(instance.recipe, context=context).data


class ShoppingListSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if ShoppingList.objects.filter(user=user,
                                       recipe__id=recipe_id).exists():
            raise ValidationError('Рецепт уже добавлен в список покупок')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowRecipeSerializer(instance.recipe, context=context).data
