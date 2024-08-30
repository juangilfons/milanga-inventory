from django.db import models
from dataclasses import dataclass
from itertools import zip_longest, repeat

# Create your models here.
class Refrigerator(models.Model):
    name = models.CharField(max_length=100)

class Column(models.Model):
    refrigerator = models.ForeignKey(Refrigerator, on_delete=models.CASCADE)
    def subcolumn_generator(self):
        subcolumns = SubColumn.objects.filter(total_tuppers__gt=0, column=self)
        total_tuppers_list = subcolumns.values_list('total_tuppers', flat=True)
        map_subcolumns_total_tuppers = dict(zip(subcolumns, total_tuppers_list))
        groups = [repeat(subcolumn, total_tuppers) for subcolumn, total_tuppers in map_subcolumns_total_tuppers.items()]

        for subcolumns in zip_longest(*groups, fillvalue=None):
            for subcolumn in subcolumns:
                if subcolumn is not None:
                    yield subcolumn.cut

class Cut(models.Model):
    name = models.CharField(max_length=100, default='test')
    milas_per_tupper = models.IntegerField()

class SubColumn(models.Model):
    column = models.ForeignKey(Column, on_delete=models.CASCADE)
    cut = models.ForeignKey(Cut, on_delete=models.CASCADE)
    total_tuppers = models.IntegerField()
    milas_tupper_in_use = models.IntegerField()
    @property
    def total_milanesas(self):
        return self.total_tuppers * self.cut
    @classmethod
    def search(cls, c):
        return cls.objects.filter(cut_name=c).count()

@dataclass
class Tupper:
   def __init__(self, subcolumn):
       self.subcolumn = subcolumn
       self.cut = subcolumn.cut
