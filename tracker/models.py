from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model) :
    # Each category is linked to a specific user

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta :
        # To ensure a user cannot have ttwo categories with same name
        unique_together = ('user','name')
        verbose_name_plural = 'Categories'

    def __str__(self) :
        return self.name


# Model for Transactions(both income and expense)
class Transaction(models.Model) :
    # Tuple to show choices for transaction type
    TRANSACTION_TYPE = [
        ('INCOME','Income'),
        ('EXPENSE','Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=7,choices=TRANSACTION_TYPE) # this type is coming from TRANSACTION_TYPE

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    # here on_delete=models.SET_NULL means when category is deleted transaction category value is set to NULL and not deleted
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True)  
    description = models.TextField(blank=True,null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) :
        return f"{self.user.username} - {self.type} - {self.amount}"
    

class Budget(models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    month = models.DateField()

    class Meta :
        pass

    def __str__(self) :
        # Example: "lucky - Groceries - August 2025 - $500.00"
        return f"{self.user.username} - {self.category.name} - {self.month.strftime('%B %Y')} - ${self.amount}"

    def save(self,*args, **kwargs) :
        # set the date to the first day of the month before saving
        self.month = self.month.replace(day=1)

        # checking for uniqueness for the given user,category,and month/year
        existing_budget = Budget.objects.filter(
            user = self.user,
            category = self.category,
            month__year = self.month.year,
            month__month = self.month.month
        ).exclude(pk=self.pk) # exclude self when updating an existing nudget

        if existing_budget.exists():
            raise ValueError(f"A budget for {self.category.name} in {self.month.strftime('%B %Y')} already exists.")
        
        super(Budget,self).save(*args,**kwargs)