from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Category,Transaction,Budget
from .forms import TransactionForm,TransactionFilterForm,BudgetForm
from django.contrib import messages
from django.db.models import Sum
import json
from django.core.paginator import Paginator
import datetime

# Create your views here.
def register(request) :
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid() :
            user = form.save()
            login(request,user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created successfully.')

            return redirect('dashboard')
        
    else :
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form' : form})  


@login_required
def catergory_list(request) :
    # if the form is submitted to create a new category
    if request.method == 'POST':
        name = request.POST.get('name')
        # create a new category associated with the logged in user

        if name :
            Category.objects.create(user=request.user, name=name)

            messages.success(request, 'New category added successfully!')
        return redirect('category_list')

    # get all the categories for the current user
    categories = Category.objects.filter(user=request.user)
    return render(request, 'tracker/category_list.html', {'categories':categories})    


@login_required
def dashboard(request):
    # 1. get all the transaction for the current user order by date
    transactions = Transaction.objects.filter(user=request.user)

    # instantiate the filter form with any GET data and the current user
    filter_form = TransactionFilterForm(request.GET, user=request.user)

    # if the form is submitted and valid, filter the transactions queryset
    if filter_form.is_valid():
        category = filter_form.cleaned_data.get('category')
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')

        if category:
            transactions = transactions.filter(category=category)
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)

    transactions = transactions.order_by('-date')

    # set up Paginator
    paginator = Paginator(transactions,10)

    # get the page number form the URL's GET parameter(e.g., ?page=2)
    page_number = request.GET.get('page')

    # get the Page object for the requested page number
    page_obj = paginator.get_page(page_number)

    # 2. calculate chart data based on all transaction

    # chart 1 : spending by category (pie chart)
    # this groups all your expenses by category and sum them up
    category_spending = transactions.filter(type='EXPENSE').values('category__name').annotate(total=Sum('amount')).order_by('-total') # here annotate is used to find the sum of a certain category

    spending_chart_labels = [item['category__name'] or 'Uncategorized' for item in category_spending]
    spending_chart_data = [float(item['total']) for item in category_spending]


    # chart 2 : income vs epense
    # this calculates the grand total of all income and all expenses
    total_income = transactions.filter(type='INCOME').aggregate(total=Sum('amount'))['total'] or 0.00
    total_expense = transactions.filter(type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0.00
    income_expense_data = [float(total_income), float(total_expense)]


    today = datetime.date.today()

    # get all budget for the user of that month and year
    current_month_budgets = Budget.objects.filter(
        user = request.user,
        month__year = today.year,
        month__month = today.month
    )

    budget_progress_list = []
    for budget in current_month_budgets :
        # for each budget calculate the total expenses in that category for month and year
        spent = Transaction.objects.filter(
            user = request.user,
            category = budget.category,
            date__year = today.year,
            date__month = today.month
        ).aggregate(total=Sum('amount'))['total'] or 0.00

        # calculate percentage
        if budget.amount > 0:
            percentage = min(int((spent/budget.amount) * 100), 100)
        else :
            percentage = 0

        budget_progress_list.append({
            'category':budget.category,
            'budget_amount':budget.amount,
            'total_spent':spent,
            'percentage':percentage,
        })    

    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']

    # 3. pass the transaction list and chart data to the template
    context = {
        'page_obj' : page_obj, 
        # 'transactions': transactions,
        'query_params' : query_params,
        'filter_form': filter_form, # <-- This line passes the form to your template
        'spending_chart_labels': json.dumps(spending_chart_labels),
        'spending_chart_data': json.dumps(spending_chart_data),
        'income_expense_data': json.dumps(income_expense_data),
        'budget_progress' : budget_progress_list,
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def add_transaction(request):
    if request.method == 'POST' :
        form = TransactionForm(request.POST, user=request.user)

        if form.is_valid() :
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('dashboard')

    else :
        form = TransactionForm(user=request.user)

    return render(request, 'tracker/add_transaction.html', {'form':form})


@login_required
def update_transaction(request,pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST' :
        form = TransactionForm(request.POST, user=request.user, instance=transaction)

        if form.is_valid() :
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('dashboard')
        
    else :
        form = TransactionForm(user=request.user, instance=transaction)

    return render(request, 'tracker/add_transaction.html', {'form':form})        


@login_required
def delete_transaction(request,pk) :
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST' :
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'tracker/delete_confirm.html.html', {'transaction':transaction})


@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user).order_by('-month')
    return render(request, 'tracker/budget_list.html', {'budgets':budgets})

@login_required
def add_budget(request) :
    if request.method == 'POST' :
        print(request.POST)
        form = BudgetForm(request.POST, user=request.user)

        if form.is_valid():
            try :
                budget = form.save(commit=False)
                budget.user = request.user
                budget.save()
                messages.success(request, 'Budget added successfully!')
                return redirect('budget_list')
            except ValueError as e :
                messages.error(request, e.message)

    else :
        form = BudgetForm(user=request.user)
    return render(request, 'tracker/add_update_budget.html', {'form':form})  


@login_required
def update_budget(request,pk) :
    budget = get_object_or_404(Budget, pk=pk, user=request.user)

    if request.method == 'POST' :
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid() :
            try:
                form.save()
                messages.success(request, 'Budget updated successfully!')
                return redirect('budget_list')
            except ValueError as e :
                messages.error(request, e.message)

    else :
        form = BudgetForm(instance=budget, user=request.user)

    return render(request, 'tracker/add_update_budget.html', {'form':form})


@login_required
def delete_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)

    if request.method == 'POST' :
        budget.delete()
        messages.success(request, 'Budget deleted successfully!')
        return redirect('budget_list')
    
    return render(request, 'tracker/delete_budget.html', {'budget':budget})