from rest_framework import mixins, viewsets


class RetriveAndListViewSet(
    mixins.ListModelMixin,
    mixins.RetriveMixin, 
    viewsets.GenericViewSet):
    pass
