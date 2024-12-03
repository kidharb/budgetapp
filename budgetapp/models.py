from django.db import models

class CSVContent(models.Model):
    field2 = models.CharField(max_length=255, blank=True, null=True)
    field3 = models.DateField(blank=True, null=True)
    field4 = models.DateTimeField(blank=True, null=True, unique=True)
    field5 = models.CharField(max_length=255, blank=True, null=True)
    field6 = models.CharField(max_length=255, blank=True, null=True)
    field7 = models.CharField(max_length=255, blank=True, null=True)
    field8 = models.CharField(max_length=255, blank=True, null=True)
    field9 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    field10 = models.CharField(max_length=255, blank=True, null=True)
    field11 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    field12 = models.CharField(max_length=255, blank=True, null=True)
