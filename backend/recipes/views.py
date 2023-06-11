from django.shortcuts import get_object_or_404
from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .mixins import RetriveAndListViewSet
from .models import Ingredient, Recipe, Tag, ShoppingList, Favorite
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
        ingredients = request.user.shopping_list.all().values_list(
            'recipe__ingredients__name',
            'recipe__ingredients__recipeingredient__amount',
            'recipe__ingredients__measurment_unit'
        )
        shopping_list = {}
        for ingredient in ingredients:
            name = ingredient[0]
            amount = ingredient[1]
            measurment_unit = ingredient[2]
            if name not in shopping_list:
                shopping_list[name] = {
                    'measurment_unit': measurment_unit,
                    'amount': amount
                }
            else:
                shopping_list[name]['amount'] += amount
        purchase = []
        for item in shopping_list:
            purchase.append(f'{item} - {shopping_list[item]["amount"]} '
                            f'{shopping_list[item]["measurment_unit"]} \n')
        response = HttpResponse(purchase, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename=purchase.txt'
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
