from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from django.db.models import Sum
from django.http import HttpResponse
from djoser.views import UserViewSet as DjoserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from recipes.serializers import (IngredientSerializer,
                                 RecipeMinifiedSerializer,
                                 RecipeReadSerializer, RecipeWriteSerializer,
                                 TagSerializer)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User
from users.serializers import SetAvatarSerializer, UserWithRecipesSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'get_link'):
            permission_classes = (AllowAny,)
        elif self.action in (
            'create',
            'favorite',
            'shopping_cart',
            'download_shopping_cart',
        ):
            permission_classes = (IsAuthenticated,)
        else:
            permission_classes = (IsAuthorOrReadOnly,)

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_to_relation(self, request, model, recipe):

        if model.objects.filter(user=request.user, recipe=recipe).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        model.objects.create(user=request.user, recipe=recipe)

        serializer = RecipeMinifiedSerializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_from_relation(self, request, model, recipe):
        relation = model.objects.filter(
            user=request.user,
            recipe=recipe
        )

        if not relation.exists():
            return Response(
                {'errors': 'Рецепта нет в списке'},
                status=status.HTTP_400_BAD_REQUEST
            )

        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()

        if request.method == 'POST':
            return self.add_to_relation(request, Favorite, recipe)

        return self.remove_from_relation(request, Favorite, recipe)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()

        if request.method == 'POST':
            return self.add_to_relation(request, ShoppingCart, recipe)

        return self.remove_from_relation(request, ShoppingCart, recipe)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        recipe_ids = ShoppingCart.objects.filter(
            'user.request.user').values_list('recipe_id', flat=True)
        ingredients = RecipeIngredient.objects.filter(
            recipe_id__in=recipe_ids).values(
            'ingredient__name, ingredient__measurement_unit').annotate(
                total_amount=Sum('amount').order_by('ingredient_name')
        )

        content = 'Список покупок\n\n'
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            amount = ingredient['total_amount']
            unit = ingredient['ingredient__measurement_unit']
            line = f'{name} = {amount} {unit}\n'
            content += line

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response

    @action(
        detail=True,
        methods=('get',),
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f'/s/{recipe.id}/')
        return Response({'short-link': short_link})


class UserViewSet(DjoserViewSet):
    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated),
        url_path='subscription'
    )
    def subscriptions(self, request):
        author_ids = Subscription.objects.filter(
            user=request.user).values_list('author_id', flat=True)
        authors = User.objects.filter(id__in=author_ids)
        page = self.paginate_queryset(authors)
        if page is not None:
            serialazer = UserWithRecipesSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serialazer.data)

        serializer = UserWithRecipesSerializer(
            authors, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=('post', 'delete',),
            permission_classes=(IsAuthenticated,), url_path='subscribe')
    def subscribe(self, request, id=None):
        author = self.get_object()
        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(
                user=request.user, author=author
            ).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(user=request.user, author=author)
            serializer = UserWithRecipesSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = Subscription.objects.filter(
            user=request.user,
            author=author
        )
        if not subscription.exist():
            return Response(
                {'errors': 'Вы не были подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=('put', 'delete',),
            permission_classes=(IsAuthenticated,),
            url_path='me/avatar')
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = SetAvatarSerializer(
                user, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
