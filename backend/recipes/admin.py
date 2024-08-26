from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline, display
from django.utils.safestring import mark_safe

from .models import (Favourite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


class RecipeIngredientsInLine(TabularInline):
    model = Recipe.ingredients.through
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'added_in_favorites',
    )
    readonly_fields = ('added_in_favorites',)
    list_filter = (
        'name',
        'author',
        'tags',
    )
    inlines = (RecipeIngredientsInLine,)

    @display(description='Количество в избранных')
    def added_in_favorites(self, obj):
        return obj.favorites.count()

    @display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ', '.join([ing.name for ing in obj.ingredient.all()])

    @display(description='Изображение')
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="60">')

    @display(description='Тэги')
    def get_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])


@admin.register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


@admin.register(Favourite)
class FavouriteAdmin(ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


@admin.register(IngredientInRecipe)
class IngredientInRecipe(ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
