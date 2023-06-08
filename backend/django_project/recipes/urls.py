from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('ingredients', views.IngredientViewSet,
                basename='ingredients')
router.register('tags', views.TagViewSet, basename='tags')


urlpatterns = [
     path('', include(router.urls)),
]