from django.db import models
from dataclasses import dataclass
from itertools import zip_longest, repeat
from django.core.exceptions import ObjectDoesNotExist
from colorfield.fields import ColorField

# Create your models here.
class Refrigerator(models.Model):
    name = models.CharField(max_length=100)

    def get_columns_tuppers(self):
        columns = []
        for column in self.column_set.all():
            column_data = {
                'column': column,
                'tuppers': list(column.column_generator())
            }
            columns.append(column_data)

        return columns
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
    reorder_threshold = models.IntegerField(default=10)
    reorder_tuppers = models.IntegerField(default=10)
    is_order_pending = models.BooleanField(default=False)
    color = ColorField(default='#FF0000')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def total_tuppers(self):
        return sum(subcolumn.total_tuppers for subcolumn in SubColumn.objects.filter(cut=self))

    @property
    def total_milas(self):
        return sum(subcolumn.total_milanesas for subcolumn in SubColumn.objects.filter(cut=self))

    def add_tuppers(self, tuppers_num, column_id):
        column = Column.objects.get(pk=column_id)
        subcolumn = SubColumn.search_column_cut(self, column)

        if not subcolumn:
            subcolumn = SubColumn.objects.create(column=column, cut=self)

        subcolumn.add_tuppers(tuppers_num)

    def sell_milas(self, milas_num):
        total_milas_available = self.total_milas

        if milas_num > total_milas_available:
            raise ValueError(f"No hay suficientes milanesas. Solo hay {total_milas_available} milanesas disponibles.")

        subcolumns = SubColumn.search_cut(self)
        total_sold = 0

        for subcolumn in subcolumns:
            milas_remaining = milas_num - total_sold
            if milas_remaining <= 0:
                break

            milas_sold_from_subcolumn = subcolumn.sell_milas(milas_remaining)
            total_sold += milas_sold_from_subcolumn

        self.check_stock_and_reorder()

    def check_stock_and_reorder(self):
        total_tuppers = sum(subcolumn.total_tuppers for subcolumn in SubColumn.objects.filter(cut=self))

        if total_tuppers < self.reorder_threshold and not self.is_order_pending:
            Order.objects.create(cut=self, tuppers_requested=self.reorder_tuppers)
            self.is_order_pending = True
            self.save()

    def __str__(self):
        return self.name

class SubColumn(models.Model):
    column = models.ForeignKey(Column, on_delete=models.CASCADE)
    cut = models.ForeignKey(Cut, on_delete=models.CASCADE)
    total_tuppers = models.IntegerField(default=0)
    milas_tupper_in_use = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.pk is not None and self.total_tuppers == 0:
            self.delete()
        else:
            if not self.milas_tupper_in_use:
                self.milas_tupper_in_use = self.cut.milas_per_tupper
            super(SubColumn, self).save(*args, **kwargs)

    @property
    def total_milanesas(self):
        return (self.total_tuppers - 1) * self.cut.milas_per_tupper + self.milas_tupper_in_use
    @classmethod
    def search_cut(cls, cut):
        return cls.objects.filter(cut=cut).order_by('id')
    @classmethod
    def search_column_cut(cls, cut, column):
        return cls.objects.filter(column=column, cut=cut).first()
    def sell_milas(self, milas_sold):
        total_milas_available = self.total_milanesas
        print(total_milas_available, milas_sold)
        if milas_sold > total_milas_available:
            milas_sold = total_milas_available

        remaining_milas = self.milas_tupper_in_use - milas_sold

        if remaining_milas > 0:
            self.milas_tupper_in_use = remaining_milas
        else:
            self.total_tuppers -= 1 + (-remaining_milas) // self.cut.milas_per_tupper
            self.milas_tupper_in_use = self.cut.milas_per_tupper - (-remaining_milas) % self.cut.milas_per_tupper
        self.save()
        return milas_sold

    def add_tuppers(self, num_tuppers):
        self.total_tuppers += num_tuppers
        self.save()

class Order(models.Model):
    cut = models.ForeignKey(Cut, on_delete=models.CASCADE)
    tuppers_requested = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    # fulfilled = models.BooleanField(default=False)
    tuppers_remaining = models.IntegerField()

    def allocate_tuppers(self, column_id, tuppers_to_add):
        if tuppers_to_add > self.tuppers_remaining:
            raise ValueError("Cannot fulfill more tuppers than remaining.")
        self.cut.add_tuppers(tuppers_to_add, column_id)
        self.tuppers_remaining -= tuppers_to_add
        self.save()

    # def fulfill(self, column_id):
    #     self.cut.add_tuppers(self.tuppers_requested, column_id)
    #     self.fulfilled = True
    #     self.cut.is_order_pending = False
    #     self.save()

    def save(self, *args, **kwargs):
        if self.pk is None:  # New order being created
            self.tuppers_remaining = self.tuppers_requested  # Initialize remaining tuppers to the requested amount
        super(Order, self).save(*args, **kwargs)


@dataclass
class Tupper:
    def __init__(self, subcolumn):
        self.subcolumn = subcolumn
        self.cut = subcolumn.cut
