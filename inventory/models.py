from django.db import models
from dataclasses import dataclass
from itertools import zip_longest, repeat
from django.core.exceptions import ObjectDoesNotExist
from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.core.validators import MinValueValidator

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
    
    def create_columns(self, num_columns, default_capacity):
        for i in range(num_columns):
            Column.objects.create(refrigerator=self, capacity=default_capacity)
    
    def __str__(self):
        return self.name


class Column(models.Model):
    refrigerator = models.ForeignKey(Refrigerator, on_delete=models.CASCADE)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])

    def column_generator(self):
        capacity = self.capacity
        subcolumns = SubColumn.objects.filter(total_tuppers__gt=0, column=self)
        total_tuppers_list = subcolumns.values_list('total_tuppers', flat=True)
        map_subcolumns_total_tuppers = dict(zip(subcolumns, total_tuppers_list))
        tuppers_count = sum(total_tuppers_list)
        empty_space = capacity - tuppers_count

        transparent_tuppers = [None] * empty_space

        groups = [repeat(subcolumn, total_tuppers) for subcolumn, total_tuppers in map_subcolumns_total_tuppers.items()]

        ordered_tuppers = transparent_tuppers + list(zip_longest(*groups, fillvalue=None))

        for tuppers in ordered_tuppers:
            if isinstance(tuppers, tuple):
                for subcolumn in tuppers:
                    if subcolumn is not None:
                        yield subcolumn.cut
            else:
                yield None  # Transparent tupper

    def has_space_for_tuppers(self, tuppers_to_add):
        # Define total capacity for this column
        total_capacity = self.capacity
        # Calculate current usage
        current_usage = sum(SubColumn.objects.filter(column=self).values_list('total_tuppers', flat=True))
        # Check if there's enough space
        return (current_usage + tuppers_to_add) <= total_capacity

    
    @classmethod
    def get_column(cls, refrigerator_id, column_pos):
        return Column.objects.filter(refrigerator_id=refrigerator_id).order_by('id')[column_pos]

    def __str__(self):
        try:
            # Get the list of column IDs for the refrigerator
            column_ids = list(Column.objects.filter(refrigerator=self.refrigerator).order_by('id').values_list('id', flat=True))
            # Find the index of the current column
            column_index = column_ids.index(self.id) + 1
            return f"Refrigerator: {self.refrigerator.name}, Column: {column_index}"
        except (ValueError, AttributeError):
            # Handle cases where the column ID is not in the list or self.id is None
            return f"Refrigerator: {self.refrigerator.name}"


class Cut(models.Model):
    name = models.CharField(max_length=100)
    milas_per_tupper = models.IntegerField()
    reorder_threshold = models.IntegerField(default=10)
    reorder_tuppers = models.IntegerField(default=10)
    is_order_pending = models.BooleanField(default=False)
    color = ColorField(default='#FF0000')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    days_until_expiration = models.IntegerField(default=180)

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
    
    def sell_milas(self, milas_num, user):
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

        ActionLog.create_action_log(
            user=user,
            obj=self,
            action_type='SALE',
            description=f"Sold {milas_num} milanesas"
        )

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
        return cls.objects.filter(cut=cut).order_by('column__refrigerator_id', 'id')
    @classmethod
    def search_column_cut(cls, cut, column):
        return cls.objects.filter(column=column, cut=cut).first()
    
    def sell_milas(self, milas_sold):
        total_milas_available = self.total_milanesas
        print(total_milas_available, milas_sold)
        if milas_sold > total_milas_available:
            milas_sold = total_milas_available

        initial_total_tuppers = self.total_tuppers
        remaining_milas = self.milas_tupper_in_use - milas_sold

        if remaining_milas > 0:
            self.milas_tupper_in_use = remaining_milas
        else:
            self.total_tuppers -= 1 + (-remaining_milas) // self.cut.milas_per_tupper
            self.milas_tupper_in_use = self.cut.milas_per_tupper - (-remaining_milas) % self.cut.milas_per_tupper
        self.save()

        tuppers_consumed = initial_total_tuppers - self.total_tuppers
        if tuppers_consumed > 0:
            self.reduce_order_allocation_tuppers(tuppers_consumed)

        return milas_sold
    
    def reduce_order_allocation_tuppers(self, tuppers_consumed):
        allocations = OrderAllocation.objects.filter(
            order__cut=self.cut,
            tuppers_allocated__gt=0
        ).order_by('order__expiration_date')

        for allocation in allocations:
            if tuppers_consumed <= 0:
                break

            if allocation.tuppers_allocated >= tuppers_consumed:
                allocation.tuppers_allocated -= tuppers_consumed
                allocation.save(update_fields=['tuppers_allocated'])
                tuppers_consumed = 0
            else:
                tuppers_consumed -= allocation.tuppers_allocated
                allocation.tuppers_allocated = 0
                allocation.save(update_fields=['tuppers_allocated'])

            if allocation.tuppers_allocated == 0:
                allocation.delete()
            
    def add_tuppers(self, num_tuppers):
        self.total_tuppers += num_tuppers
        self.save()
    
    
class Order(models.Model):
    cut = models.ForeignKey(Cut, on_delete=models.CASCADE)
    tuppers_requested = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    # fulfilled = models.BooleanField(default=False)
    tuppers_remaining = models.IntegerField()
    scheduled_date = models.DateTimeField(blank=True, null=True)
    expiration_date = models.DateTimeField(blank=True, null=True)


    def allocate_tuppers(self, column_id, tuppers_to_add, user):
        if tuppers_to_add > self.tuppers_remaining:
            raise ValueError("Cannot fulfill more tuppers than remaining.")
        column = Column.objects.get(id=column_id)

        self.cut.add_tuppers(tuppers_to_add, column_id)
        self.tuppers_remaining -= tuppers_to_add

        allocation, created = OrderAllocation.objects.get_or_create(
            order=self,
            column=column,
            defaults={'tuppers_allocated': tuppers_to_add}
        )
        if not created:
            allocation.tuppers_allocated += tuppers_to_add
            allocation.save()

        if (self.tuppers_remaining == 0):
            self.cut.is_order_pending = False
            self.cut.save()
        self.cut.check_stock_and_reorder()
        self.save(update_remaining=True)
        ActionLog.create_action_log(
            user=user,
            obj=self,
            action_type='FULFILLMENT',
            description=f"Allocated {tuppers_to_add} tuppers to column {column_id}"
        )

    # def fulfill(self, column_id):
    #     self.cut.add_tuppers(self.tuppers_requested, column_id)
    #     self.fulfilled = True
    #     self.cut.is_order_pending = False
    #     self.save()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        update_remaining = kwargs.pop('update_remaining', False)

        # Check if this is a new order or being saved through the admin site
        if is_new or not update_remaining:
            # Set tuppers_remaining to tuppers_requested
            self.tuppers_remaining = self.tuppers_requested

        if is_new:
            # Mark the related cut as having a pending order
            self.cut.is_order_pending = True
            self.cut.save()

            # Set scheduled_date to the next Tuesday if not already set
            if not self.scheduled_date:
                now = timezone.now()
                days_until_tuesday = 8 - now.weekday()
                self.scheduled_date = now + timedelta(days=days_until_tuesday)

        # Set expiration_date based on scheduled_date and days_until_expiration
        if self.scheduled_date and self.cut.days_until_expiration:
            self.expiration_date = self.scheduled_date + timedelta(days=self.cut.days_until_expiration)

        # Call the original save method
        super(Order, self).save(*args, **kwargs)

    def get_column_allocations(self):
        # Retrieve all allocations related to this order
        return OrderAllocation.objects.filter(order=self)
    
    def __str__(self):
        return f'Orden de {self.cut.name}'

class ActionLog(models.Model):
    ACTION_CHOICES = [
        ('FULFILLMENT', 'Supplier Order Fulfillment'),
        ('SALE', 'Sale of Milanesas'),
        ('ADMIN_ACTION', 'Inventory Management'),
    ]

    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('EMPLOYEE', 'Employee'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    object_repr = models.CharField(max_length=200)
    action_description = models.TextField()
    action_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} ({self.action_time})"

    def create_action_log(user, obj, action_type, description):
        user_role = 'ADMIN' if user.is_superuser else 'EMPLOYEE'
        ActionLog.objects.create(
            user=user,
            user_role=user_role,
            action_type=action_type,
            object_repr=str(obj),
            action_description=description,
            action_time=timezone.now()
        )

class OrderAllocation(models.Model):
    order = models.ForeignKey(Order, related_name='allocations', on_delete=models.CASCADE)
    column = models.ForeignKey(Column, on_delete=models.CASCADE)
    tuppers_allocated = models.IntegerField()


