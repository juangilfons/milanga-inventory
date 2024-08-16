from django.db import models

# Create your models here.
class Refrigerator(models.Model):
    name = models.CharField(max_length=100)

class Column(models.Model):
    refrigerator = models.ForeignKey(Refrigerator, on_delete=models.CASCADE)

class Cut(models.Model):
    milas_per_tupper = models.IntegerField()

class SubColumn(models.Model):
    column = models.ForeignKey(Column, on_delete=models.CASCADE)
    cut = models.ForeignKey(Cut, on_delete=models.CASCADE)
    total_tuppers = models.IntegerField()
    milas_tupper_in_use = models.IntegerField()
    @property
    def total_milanesas(self):
        return self.total_tuppers * self.cut
    def count(self):
        return self.count()