from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import (CASCADE, CharField, ForeignKey, ImageField,
                              ManyToManyField, Model,
                              PositiveSmallIntegerField, SlugField, TextField,
                              UniqueConstraint)

User = get_user_model()


class Tag(Model):
    name = CharField(
        verbose_name='Название тега',
        help_text='Название тега',
        unique=True,
        max_length=settings.MAX_LENGHT_TAG_NAME
    )
    color = CharField(
        verbose_name='Цвет для тега в HEX',
        help_text='Цвет для тегов HEX',
        unique=True,
        max_length=settings.MAX_LENGHT_TAG_COLOR,
        validators=[
            RegexValidator(
                regex=settings.REQES,
                message='Введите значение в формате HEX!',
            )
        ]
    )
    slug = SlugField(
        verbose_name='Идентификатор тега',
        help_text='Идентификатор тега',
        unique=True,
        max_length=settings.MAX_LENGHT_TAG_SLUG
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(Model):
    name = CharField(
        verbose_name='Название',
        help_text='Название',
        max_length=settings.MAX_LENGHT_INGREDIENTS_NAME
    )
    measurement_unit = CharField(
        verbose_name='Единица измерения',
        help_text='Единица измерения',
        max_length=settings.MAX_LENGHT_INGREDIENTS_MEASUREMENT_UNIT
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit',
            ),
        )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(Model):
    tags = ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        help_text='Теги'
    )
    author = ForeignKey(
        User,
        related_name='recipes',
        on_delete=CASCADE,
        null=True,
        verbose_name='Автор',
        help_text='Автор'
    )
    ingredients = ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Ингредиенты'
    )
    name = CharField(
        verbose_name='Название рецепта',
        help_text='Название рецепта',
        max_length=settings.MAX_LENGHT_RECIPE_NAME
    )
    image = ImageField(
        verbose_name='Изображение рецепта',
        help_text='Изображение рецепта',
        upload_to='recipes/'
    )
    text = TextField(
        verbose_name='Описание',
        help_text='Описание'
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                settings.MIN_VALUE_COOKING_TIME,
                message='Минимальное время приготовления 1 минута!'
            )
        ]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favourite(Model):
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
        help_text='Пользователь'
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
        help_text='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingCart(Model):
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
        help_text='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
        help_text='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Список покупок'


class IngredientInRecipe(Model):
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт',
        help_text='Рецепт'
    )
    ingredient = ForeignKey(
        Ingredient,
        on_delete=CASCADE,
        verbose_name='Ингредиент',
        help_text='Ингредиент'
    )
    amount = PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Количество',
        validators=[
            MinValueValidator(
                settings.MIN_VALUE_AMOUNT_INGREDIENTS,
                message='Минимальное количество 1!'
            )
        ]
    )

    class Meta:
        verbose_name = 'Рецепт с ингридиентом'
        verbose_name_plural = 'Рецепты с ингридиентами'

    def __str__(self):
        return (
            f'''
            {self.ingredient.name}
            ({self.ingredient.measurement_unit}) -
            {self.amount}'''
        )
