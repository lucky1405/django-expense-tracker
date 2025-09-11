from django import forms
from .models import Category,Transaction,Budget

class TransactionForm(forms.ModelForm):
    class Meta :
        model = Transaction

        # we only want the user to fill out these feilds
        fields = ['type','amount','date','category','description']

        widgets = {
            'date' : forms.DateInput(attrs={'type':'date'}),
        }

    # We override the form's init method to customize it
    def __init__(self, *args, **kwargs):
        # We need to get the user to filter categories
        user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        if user:
            # Filter the category dropdown to only show the user's own categories
            self.fields['category'].queryset = Category.objects.filter(user=user)


class TransactionFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        label='Category',
        empty_label='All Categories'
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Start Date'
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='End Date'
    )

    def __init__(self, *args, **kwargs):
        # Use the safer version of pop, just like in your other form
        user = kwargs.pop('user', None)
        super(TransactionFilterForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
        else:
            # This is a safeguard in case the user is not passed from the view
            raise ValueError("TransactionFilterForm requires a 'user' keyword argument.")
        
        self.fields['start_date'].widget.attrs.update({'class': 'form-control', 'placeholder': ' '})
        self.fields['end_date'].widget.attrs.update({'class': 'form-control', 'placeholder': ' '})
        self.fields['category'].widget.attrs.update({'class': 'form-select'})


# tracker/forms.py

class BudgetForm(forms.ModelForm):
    # We explicitly define the 'month' field here to customize it
    month = forms.DateField(
        # This is the critical line that creates the month picker
        widget=forms.DateInput(attrs={'type': 'month', 'class': 'js-month-picker'}),

        # This line tells Django how to understand the picker's data
        input_formats=['%Y-%m'],
        label="Month"
    )

    class Meta:
        model = Budget
        # 'month' is removed from here because we defined it above
        fields = ['category', 'amount','month']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(BudgetForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)