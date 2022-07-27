import itertools

from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from foodgram.settings import FILE_NAME
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from recipes.serializers import RecipePartialSerializer
from api.mixins import RetrieveListViewSet
from api.filters import IngredientsFilter, RecipeFilter
from api.permissions import IsAuthOwnerOrReadOnly
from api.serializers import (IngredientsSerializer, RecipesCreateSerializer,
                             RecipesSerializer, TagsSerializer)

CONTENT_TYPE = 'application/pdf'


class IngredientsViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter
    pagination_class = None


class TagsViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipesCreateSerializer
        return RecipesSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(permissions.IsAuthenticated)
    )
    def download_shopping_cart(self, request):
        user_recipes = Recipe.objects.filter(shopping_cart__user=request.user)
        if not user_recipes:
            error = {'errors': 'Список рецептов пуст'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        ingredients = user_recipes.values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).order_by(
            'ingredients__name'
        ).annotate(Sum('amount'))
        response = HttpResponse(content_type=CONTENT_TYPE)
        response['Content-Disposition'] = (
            f'attachment; filename = {FILE_NAME}')
        canvas = Canvas(response)
        pdfmetrics.registerFont(TTFont('Roboto', 'Roboto.ttf'))
        canvas.setFont('Roboto', 50)
        canvas.drawString(100, 750, 'Список покупок:')
        canvas.setFont('Roboto', 30)
        counter = itertools.count(650, -50)
        for k, v in ingredients.items():
            if int(round(v, 2) % 1 * 100) == 0:
                v = int(v)
            height = next(counter)
            canvas.drawString(50, height, f'-  {k} - {v}')
        canvas.save()
        return response


class FavoriteShoppingCartView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = {
        'favorite': Favorite.objects,
        'shopping_cart': ShoppingCart.objects
    }

    def post(self, request, recipe_id):
        name_url = request.resolver_match.url_name
        recipe = get_object_or_404(Recipe, id=recipe_id)
        double = self.queryset[name_url].filter(
            user=request.user,
            recipe=recipe
        ).exists()
        if double:
            error = {'errors': 'Рецепт уже добавлен'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        self.queryset[name_url].create(user=request.user, recipe=recipe)
        serializer = RecipePartialSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        name_url = request.resolver_match.url_name
        recipe = get_object_or_404(Recipe, id=recipe_id)
        try:
            obj = self.queryset[name_url].get(user=request.user, recipe=recipe)
        except ObjectDoesNotExist:
            error = {'errors': 'Рецепт не найден в списке'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
