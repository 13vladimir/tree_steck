from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import CharField, ModelSerializer
from rest_framework.status import HTTP_400_BAD_REQUEST

from recipes.models import (Favourite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request is not None and request.user.is_authenticated
                and obj.subscribing.filter(user_id=request.user.id).exists())


class SubscribeSerializer(CustomUserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except ValueError:
                return ('Ошибка значения: limit должен быть целым числом.')
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data


class SubscribePostSerializer(ModelSerializer):
    user_id = IntegerField()
    author_id = IntegerField()

    class Meta:
        model = Subscribe
        fields = ('user_id', 'author_id')

    def validate(self, data):
        user = User.objects.get(id=data.get('user_id'))
        author = User.objects.get(id=data.get('author_id'))
        if author == user:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=HTTP_400_BAD_REQUEST
            )
        if user.subscriber.filter(author=author).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=HTTP_400_BAD_REQUEST
            )
        return data

    def to_representation(self, instance):
        serializer = SubscribeSerializer(instance.author, context=self.context)
        return serializer.data


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeShortSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class GetAmountIngredientSerializer(ModelSerializer):
    id = IntegerField(
        source='ingredient.id',
        read_only=True
    )
    name = CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = GetAmountIngredientSerializer(source='ingredient_list',
                                                many=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request is not None and request.user.is_authenticated
                and request.user.favorites.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request is not None and request.user.is_authenticated
                and request.user.shopping_cart.filter(recipe=obj).exists())


class IngredientInRecipeWriteSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField(min_value=settings.MIN_VAL_AMOUNT,
                          max_value=settings.MAX_VAL_AMOUNT)

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'amount'
        )


class RecipeWriteSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                  many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField()
    cooking_time = IntegerField(min_value=settings.MIN_VAL_COOK,
                                max_value=settings.MAX_VAL_COOK)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_tags(self, value):
        if not value:
            raise ValidationError(
                'Выбире один тег!'
            )
        if len(value) != len(set(value)):
            raise ValidationError(
                'Теги не должны повторяться!'
            )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(
                'Нужно добавить хотя бы один ингредиент!'
            )
        ingredients = set(item['id'] for item in value)
        if len(ingredients) != len(value):
            raise ValidationError(
                'Нельзя добавить два одинаковых ингридиента!'
            )
        return value

    @staticmethod
    def create_ingredients_amounts(ingredients, recipe):
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe, ingredients=ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(
            recipe=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data


class CreateBaseSerializer(ModelSerializer):
    user_id = IntegerField()
    recipe_id = IntegerField()
    error_message: str

    def __init__(self, data, error_message):
        super().__init__(data=data)
        self.error_message = error_message

    def to_representation(self, instance):
        serializer = RecipeShortSerializer(
            instance.recipe, context=self.context
        )
        return serializer.data

    def validate(self, data):
        if self.Meta.model.objects.filter(
            user_id=data['user_id'],
            recipe_id=data['recipe_id']
        ).exists():
            raise ValidationError(
                detail=self.error_message,
                code=HTTP_400_BAD_REQUEST
            )
        return data


class FavouriteSerializer(CreateBaseSerializer):
    class Meta:
        model = Favourite
        fields = ('user_id', 'recipe_id')


class ShoppingCartSerializer(CreateBaseSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user_id', 'recipe_id')
