from django.shortcuts import get_object_or_404
from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum

from .mixins import RetriveAndListViewSet
from .models import (Ingredient, Recipe,
                     Tag, ShoppingList, Favorite, RecipeIngredient)
from .filters import IngredientFilter, RecipeFilter
from .paginators import CustomPageNumberPaginator
from .permissions import IsAuthorOrAdmin
from .serializers import (
    AddRecipeSerializer, FavouriteSerializer, IngredientSerializer,
    ShoppingListSerializer, ShowRecipeFullSerializer, TagSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = ShowRecipeFullSerializer
    permission_classes = [IsAuthorOrAdmin]
    filter_backends = [DjangoFilterBackend]
    pagination_class = CustomPageNumberPaginator
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ShowRecipeFullSerializer
        return AddRecipeSerializer

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthorOrAdmin])
    def favorite(self, request, pk):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = FavouriteSerializer(data=data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthorOrAdmin])
    def shopping_cart(self, request, pk):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = ShoppingListSerializer(data=data,
                                            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_list = get_object_or_404(ShoppingList,
                                          user=user, recipe=recipe)
        shopping_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_lists__user=request.user
        ).values(
            "ingredient__name",
            "ingredient__measurement_unit"
        ).annotate(
            amount=Sum('amount')
        )

        text_result = ''
        for product in ingredients:
            ingredient_name = product['ingredient__name']
            measurement_unit = product['ingredient__measurement_unit']
            amount = product['amount']
            text_result += f'{ingredient_name} ({measurement_unit}) {amount}\n'

        response = HttpResponse(text_result, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=shop_list.txt'
        return response


class IngredientViewSet(RetriveAndListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    pagination_class = None
    filterset_class = IngredientFilter


class TagViewSet(RetriveAndListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
