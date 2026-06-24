from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from recipes.models import Favorite, Recipe, RecipeIngredient, ShoppingCart, Tag


class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('author', 'name', 'cooking_time', 'image', 'tags', 'text')

    def clean_cooking_time(self):
        cooking_time = self.cleaned_data.get('cooking_time')

        if cooking_time < 1:
            raise forms.ValidationError(
                'Время приготовления должно быть не меньше 1 минуты'
            )

        return cooking_time

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')

        if not tags:
            raise forms.ValidationError(
                'Нужно выбрать хотя бы один тег'
            )

        return tags


class RecipeIngredientInlineFormSet(BaseInlineFormSet):

    def clean(self):
        super().clean()

        ingredients = []

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue

            if form.cleaned_data.get('DELETE'):
                continue

            ingredient = form.cleaned_data.get('ingredient')
            amount = form.cleaned_data.get('amount')

            if ingredient:
                ingredients.append(ingredient)

            if amount < 1:
                raise forms.ValidationError(
                    'Количество ингредиента должно быть не меньше 1'
                )

        if not ingredients:
            raise forms.ValidationError(
                'Нужно добавить хотя бы один ингредиент'
            )

        if len(ingredients) != len(set(ingredients)):
            raise forms.ValidationError(
                'Ингредиенты не должны повторяться'
            )


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    formset = RecipeIngredientInlineFormSet
    extra = 1
    min_num = 1
    validate_min = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    form = RecipeAdminForm
    inlines = (RecipeIngredientInline,)
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


admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
