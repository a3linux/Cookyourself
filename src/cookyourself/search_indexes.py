from haystack import indexes

from cookyourself.models import Dish


class DishIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    description = indexes.CharField(model_attr='description')

    def get_model(self):
        return Dish

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
