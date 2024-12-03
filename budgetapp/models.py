from django.db import models

class CSVContent(models.Model):
    account_number = models.CharField(max_length=255, blank=True, null=True)
    posting_date = models.DateField(blank=True, null=True)
    transaction_date = models.DateTimeField(blank=True, null=True, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    original_description = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    money_out = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    money_in = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    group = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Ensure the group is set to "Transfers" if the category is "Transfers"
        if self.category == "Transfers":
            self.group = "Transfers"
        if self.category == "Fees":
            self.group = "Recurring"
        if self.category == "Salary" or self.category == "Other Income":
            self.group = "Income"
        if (self.category == "Groceries" or
            self.category == "Takeaways" or
            self.category == "Restaurants" or
            self.category == "Fuel"):

            self.group = "Day to Day"
        super().save(*args, **kwargs)
