from django.contrib import admin

from .models import Amount, Favorite, Ingredient, Recipe, ShoppingCart, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Избранное', {
            'classes': ('collapse',),
            'fields': ['favorites_count'],
        }),
        (None, {
            'fields': ['name', 'text', 'cooking_time', 'image', 'ingredients',
                       'tags']
        }),
        ('Изменить автора', {
            'classes': ('collapse',),
            'fields': ['author'],
        }),
    )
    readonly_fields = ('favorites_count',)
    list_display = ('id', 'name', 'author')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'author__username')
    list_filter = ('tags', 'author')

    def favorites_count(self, instance):
        return Favorite.objects.filter(recipe=instance).count()

    favorites_count.short_description = 'Добавлен в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('id', 'name')
    search_fields = ('name__icontains',)


@admin.register(Amount)
class AmountAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'ingredient')
    list_display_links = ('id', 'amount', 'ingredient')
    search_fields = ('ingredient',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
