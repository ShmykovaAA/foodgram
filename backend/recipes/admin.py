from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)

@admin.register(Ingredient)
class Ingredient(admin.ModelAdmin):
    list_display =('id', 'name', 'measurement_unit',)
    search_fields = ('name',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author_username',
        'favorites_count',
    )
    search_fields = (
        'name',
        'author__username',
        'author__email',
        'author__first_name',
        'author__last_name',
    )
    list_filter = (
        'tags',
    )
    filter_horizontal = (
        'tags',
    )
    readonly_fields = (
        'favorites_count',
    )

    @admin.display(description='Добавлений в избранное')
    def favorites_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    @admin.display(description='Автор')
    def author_username(self, obj):
        return obj.author.username

@admin.register(RecipeIngredient)
@admin.register(Favorite)
@admin.register(ShoppingCart)
@admin.register(Tag)