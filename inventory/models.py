from django.db import models
from dataclasses import dataclass
from itertools import zip_longest, repeat
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.
class Refrigerator(models.Model):
    name = models.CharField(max_length=100)

class Column(models.Model):
    refrigerator = models.ForeignKey(Refrigerator, on_delete=models.CASCADE)
    def column_generator(self):
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
    reorder_threshold = models.IntegerField()
    reorder_tuppers = models.IntegerField()
    is_order_pending = models.BooleanField(default=False)

    def add_tuppers(self, tuppers_num, column_id):
        column = Column.objects.get(pk=column_id)
        subcolumn = SubColumn.search_column_cut(self, column)

        if not subcolumn:
            SubColumn.objects.create(column=column, cut=self)

        subcolumn.add_tuppers(tuppers_num)
    
    def sell_milas(self, milas_num):
        subcolumn = SubColumn.search_cut(self)

        if not subcolumn:
            raise ObjectDoesNotExist("No hay milanesas disponibles.")
        
        subcolumn.sell_milas(milas_num)
        self.check_stock_and_reorder()
    
    def check_stock_and_reorder(self):
        total_stock = sum(subcolumn.total_milanesas for subcolumn in SubColumn.objects.filter(cut=self))

        if total_stock < self.reorder_threshold and not self.is_order_pending:
            Order.objects.create(cut=self, tuppers_requested=self.reorder_tuppers)
            self.is_order_pending = True

class SubColumn(models.Model):
    column = models.ForeignKey(Column, on_delete=models.CASCADE)
    cut = models.ForeignKey(Cut, on_delete=models.CASCADE)
    total_tuppers = models.IntegerField(default=0)
    milas_tupper_in_use = models.IntegerField(default=cut.milas_per_tupper)

    def save(self, *args, **kwargs):
        if self.total_tuppers == 0:
            self.delete()
        else:
            super().save(*args, **kwargs)
    @property
    def total_milanesas(self):
        return self.total_tuppers * self.cut.milas_per_tupper
    @classmethod
    def search_cut(cls, cut):
        return cls.objects.filter(cut=cut).first()
    @classmethod
    def search_column_cut(cls, cut, column):
        return cls.objects.filter(column=column, cut=cut).first()
    def sell_milas(self, milas_sold):
        total_milas_available = (self.total_tuppers - 1) * self.cut.milas_per_tupper + self.milas_tupper_in_use
        if milas_sold > total_milas_available:
            raise ValueError("No hay milanesas suficientes.")

        remaining_milas = self.milas_tupper_in_use - milas_sold

        if remaining_milas > 0:
            self.milas_tupper_in_use = remaining_milas
        else:
            self.total_tuppers -= 1 + (-remaining_milas) // self.cut.milas_per_tupper
            self.milas_tupper_in_use = self.cut.milas_per_tupper - (-remaining_milas) % self.cut.milas_per_tupper
        self.save()

    def add_tuppers(self, num_tuppers):
        self.total_tuppers += num_tuppers
        self.save()

class Order(models.Model):
    cut = models.ForeignKey(Cut, on_delete=models.CASCADE)
    tuppers_requested = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    fulfilled = models.BooleanField(default=False)

    def fulfill(self, column_id):
        self.cut.add_tuppers(self.tuppers_requested, column_id)
        self.fulfilled = True
        self.cut.is_order_pending = False
        self.save()

@dataclass
class Tupper:
   def __init__(self, subcolumn):
       self.subcolumn = subcolumn
       self.cut = subcolumn.cut
