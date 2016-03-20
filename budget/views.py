from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404

from .models import Budget, BudgetUser
from .models import ExpenseCategory, IncomeCategory, FinancialAccountCategory, Bank
from .models import Acc, ExpenseAccount, MoneyAccount, IncomeAccount, AssetAccount, LiabilityAccount
from .models import Expense, ExpenseItem, MoneyTransfer, Income, JournalRecord, InitialBalance
from .models import ReportLine, ReportGroupLines, ReportIncome, ReportBalance

from .forms import FormBudgetNew, FormBudgetUser
from .forms import FormCatExpenseNew, FormCatIncomeNew, FormCatFinAccountNew, FormBankNew
from .forms import FormAccExpenseNew, FormAccIncomeNew, FormAccMoneyNew, FormAccAssetNew, FormAccLiabilityNew
from .forms import FormExpenseNew, FormExpenseItemNew, FormIncomeNew, FormMoneyTransferNew, FormInitBalance
from .forms import FormReportProfitSetup, FormReportBalanceSetup

from datetime import date, timedelta
# Create your views here.

@login_required
def index(request):
	if BudgetUser.objects.filter(user = request.user, is_main=True).count():
		b = BudgetUser.objects.get(user = request.user, is_main=True)
		return HttpResponseRedirect("/budget/" + str(b.budget.id) + "/")
	return HttpResponseRedirect("/budget/all/")

@login_required
def budget_all(request):
	if request.method == "POST":
		f = FormBudgetNew(request.POST)
		if f.is_valid():
			b = f.save(commit=False)
			b.user_owner = request.user
			b.save()
	budget_set = Budget.objects.filter(user_owner = request.user)
	budget_user_set = BudgetUser.objects.filter(user = request.user)
	form_budget_new = FormBudgetNew
	return render(request, 'budget/budgets_all.html', {'budget_user_set': budget_user_set, 'budget_set': budget_set, 'form_budget_new': form_budget_new })
	
@login_required
def budget(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		ex_drafts = Expense.objects.filter(budget=b, is_saved=False)
		return render(request, 'budget/budget.html', {'budget': b, 'ex_drafts': ex_drafts})
	return HttpResponseRedirect("/budget/")

@login_required
def budget_edit(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	if BudgetUser.objects.filter(budget=b, user=request.user).count():
		if request.method == "POST":
			if request.POST['form_id'] == "budget":
				f = FormBudgetNew(request.POST)
				if f.is_valid():
					entity = f.save(commit=False)
					b.name = entity.name
					b.save()
					if request.POST['is_main'] == "MAIN":
						b_current_main = BudgetUser.objects.get(user=request.user, is_main=True)
						b_current_main.is_main = False
						b_current_main.save()
						b_new_main = BudgetUser.objects.get(user=request.user, budget=b)
						b_new_main.is_main = True
						b_new_main.save()
						
			if request.POST['form_id'] == "user_budget":
				f = FormBudgetUser(request.POST)
				if f.is_valid():
					u_name = f.cleaned_data['user_name']
					if User.objects.filter(username=u_name).count():
						u = User.objects.get(username=u_name)
						if not BudgetUser.objects.filter(budget=b,user=u).count():
							new_bu_is_main = False
							if not BudgetUser.objects.filter(user=u).count():
								new_bu_is_main = True
							new_bu = BudgetUser(user=u,budget=b,is_main=new_bu_is_main)
							new_bu.save()
							
		budget_user_set = BudgetUser.objects.filter(budget=b).exclude(user=request.user)
		bu = BudgetUser.objects.get(budget=b, user=request.user)
		form_budget = FormBudgetNew(instance=b)
		form_user_budged = FormBudgetUser
		return render(request, 'budget/budget_edit.html', {'budget': b, 'form_budget': form_budget, 'budget_user_set': budget_user_set, 'form_user_budged':form_user_budged, 'bu': bu})
	return HttpResponseRedirect("/budget/")
	
@login_required
def cat_expenses(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormCatExpenseNew(request.POST)
			if f.is_valid():
				e = f.save(commit=False)
				e.budget = b
				e.save()
		items = ExpenseCategory.objects.filter(budget=b)
		form_cat_expense_new = FormCatExpenseNew
		return render(request, 'budget/cat_expenses.html', {'budget': b, 'items': items, 'form_cat_expense_new': form_cat_expense_new})
	return HttpResponseRedirect("/budget/")
	
@login_required
def cat_income(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormCatIncomeNew(request.POST)
			if f.is_valid():
				e = f.save(commit=False)
				e.budget = b
				e.save()
		items = IncomeCategory.objects.filter(budget=b)
		form_cat_income_new = FormCatIncomeNew
		return render(request, 'budget/cat_income.html', {'budget': b, 'items': items, 'form_cat_income_new': form_cat_income_new})
	return HttpResponseRedirect("/budget/")

@login_required
def cat_fin_account(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormCatFinAccountNew(request.POST)
			if f.is_valid():
				e = f.save(commit=False)
				e.budget = b
				e.save()
		items = FinancialAccountCategory.objects.filter(budget=b)
		form_cat_fin_account_new = FormCatFinAccountNew
		return render(request, 'budget/cat_fin_account.html', {'budget': b, 'items': items, 'form_cat_fin_account_new': form_cat_fin_account_new})
	return HttpResponseRedirect("/budget/")
	
@login_required
def banks(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormBankNew(request.POST)
			if f.is_valid():
				e = f.save(commit=False)
				e.budget = b
				e.save()
		items = Bank.objects.filter(budget=b)
		form_bank_new = FormBankNew
		return render(request, 'budget/banks.html', {'budget': b, 'items': items, 'form_bank_new': form_bank_new})
	return HttpResponseRedirect("/budget/")
	
#ExpenseCategory, IncomeCategory, FinancialAccountCategory, Bank
#FormAccExpenseNew, FormAccIncomeNew, FormAccMoneyNew, FormAccAssetNew, FormAccLiabilityNew
#Acc, ExpenseAccount, MoneyAccount, IncomeAccount, AssetAccount, LiabilityAccount

@login_required
def acc_expense(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormAccExpenseNew(request.POST)
			if f.is_valid():
				try:
					e = f.save(commit=False)
					e.budget = b
					c = ExpenseCategory.objects.get(pk=request.POST['cat_id'])
					e.category = c
					e.save()
				except:
					pass
					#return HttpResponseRedirect("/budget/" + str(b.id) + "/")
		items = ExpenseAccount.objects.filter(budget=b, is_archived=False)
		cat = ExpenseCategory.objects.filter(budget=b)
		form_acc_expense_new = FormAccExpenseNew
		return render(request, 'budget/acc_expense.html', {'budget': b, 'items': items, 'form_acc_expense_new': form_acc_expense_new, 'cat': cat})
	return HttpResponseRedirect("/budget/")

@login_required
def acc_income(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormAccIncomeNew(request.POST)
			if f.is_valid():
				try:
					e = f.save(commit=False)
					e.budget = b
					c = IncomeCategory.objects.get(pk=request.POST['cat_id'])
					e.category = c
					e.save()
				except:
					pass
					#return HttpResponseRedirect("/budget/" + str(b.id) + "/")
		items = IncomeAccount.objects.filter(budget=b, is_archived=False)
		cat = IncomeCategory.objects.filter(budget=b)
		form_acc_income_new = FormAccIncomeNew
		return render(request, 'budget/acc_income.html', {'budget': b, 'items': items, 'form_acc_income_new': form_acc_income_new, 'cat': cat})
	return HttpResponseRedirect("/budget/")
	
@login_required
def acc_money(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormAccMoneyNew(request.POST)
			if f.is_valid():
				try:
					e = f.save(commit=False)
					e.budget = b
					c = FinancialAccountCategory.objects.get(pk=request.POST['cat_id'])
					bnk = Bank.objects.get(pk=request.POST['bank_id'])
					e.category = c
					e.bank = bnk
					e.save()
				except:
					pass
					#return HttpResponseRedirect("/budget/" + str(b.id) + "/")
		items = MoneyAccount.objects.filter(budget=b, is_archived=False)
		cat = FinancialAccountCategory.objects.filter(budget=b)
		banks = Bank.objects.filter(budget=b)
		form_acc_money_new = FormAccMoneyNew
		return render(request, 'budget/acc_money.html', {'budget': b, 'items': items, 'form_acc_money_new': form_acc_money_new, 'cat': cat, 'banks': banks})
	return HttpResponseRedirect("/budget/")
	
@login_required
def acc_asset(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormAccAssetNew(request.POST)
			if f.is_valid():
				try:
					e = f.save(commit=False)
					e.budget = b
					e.save()
				except:
					pass
					#return HttpResponseRedirect("/budget/" + str(b.id) + "/")
		items = AssetAccount.objects.filter(budget=b, is_archived=False)
		form_acc_asset_new = FormAccAssetNew
		return render(request, 'budget/acc_asset.html', {'budget': b, 'items': items, 'form_acc_asset_new': form_acc_asset_new})
	return HttpResponseRedirect("/budget/")
	
@login_required
def acc_liability(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormAccLiabilityNew(request.POST)
			if f.is_valid():
				try:
					e = f.save(commit=False)
					e.budget = b
					e.save()
				except:
					pass
		items = LiabilityAccount.objects.filter(budget=b, is_archived=False)
		form_acc_liability_new = FormAccLiabilityNew
		return render(request, 'budget/acc_liability.html', {'budget': b, 'items': items, 'form_acc_liability_new': form_acc_liability_new})
	return HttpResponseRedirect("/budget/")

@login_required
def expense_new_aux(request):
	bu = BudgetUser.objects.filter(user=request.user,is_main=True)
	b = bu[0].budget
	return HttpResponseRedirect("/budget/" + str(b.id) + "/expense/new/")

@login_required
def income_new_aux(request):
	bu = BudgetUser.objects.filter(user=request.user,is_main=True)
	b = bu[0].budget
	return HttpResponseRedirect("/budget/" + str(b.id) + "/income/new/")
	
@login_required
def expense_new(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormExpenseNew(request.POST)
			if f.is_valid():
				try:
					e = f.save(commit=False)
					e.budget = b
					m = MoneyAccount.objects.get(pk=request.POST['money_acc_id'])
					e.money_account = m
					e.save()
					return HttpResponseRedirect("/budget/" + str(b.id) + "/expense/" + str(e.id) + "/")
				except:
					pass
		money_accs = MoneyAccount.objects.filter(budget=b, is_archived=False)
		form_expense_new = FormExpenseNew()
		items = Expense.objects.filter(budget=b)
		return render(request, 'budget/expense_new.html', {'budget': b, 'money_accs': money_accs, 'form_expense_new': form_expense_new, 'items': items})
	return HttpResponseRedirect("/budget/")
	
@login_required
def expenses(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		items = Expense.objects.filter(budget=b)
		items = sorted(items, key=lambda x: x.payment_date, reverse=True)
		return render(request, 'budget/expenses.html', {'budget': b, 'items': items})
	return HttpResponseRedirect("/budget/")
	
@login_required
def incomes(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		items = Income.objects.filter(budget=b)
		items = sorted(items, key=lambda x: x.payment_date, reverse=True)
		return render(request, 'budget/incomes.html', {'budget': b, 'items': items})
	return HttpResponseRedirect("/budget/")
	
@login_required
def money_transfers(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		items = MoneyTransfer.objects.filter(budget=b)
		items = sorted(items, key=lambda x: x.payment_date, reverse=True)
		return render(request, 'budget/transfers.html', {'budget': b, 'items': items})
	return HttpResponseRedirect("/budget/")
	
@login_required
def expense_edit(request, budget_id, expense_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			if request.POST['form_id'] == "expense":
				f = FormExpenseNew(request.POST)
				if f.is_valid():
					try:
						e = f.save(commit=False)
						e.budget = b
						m = MoneyAccount.objects.get(pk=request.POST['money_acc_id'])
						e.money_account = m
						
						ex = Expense.objects.get(pk=expense_id)
						ex.money_account = e.money_account
						ex.shop_name = e.shop_name
						ex.comment = e.comment
						ex.payment_date = e.payment_date
						ex.save()
					except:
						pass
			elif request.POST['form_id'] == "expense_item_new":
				f = FormExpenseItemNew(request.POST)
				if f.is_valid():
					try:
						e = f.save(commit=False)
						ex = Expense.objects.get(pk=expense_id)
						e.expense = ex
						a = ExpenseAccount.objects.get(pk=request.POST['expense_acc_id'])
						e.expense_account = a
						e.save()
						ex.save()
					except:
						pass
		ex = Expense.objects.get(pk=expense_id)
		if (ex.budget != b):
			return HttpResponseRedirect("/budget/")
		money_accs = MoneyAccount.objects.filter(budget=b, is_archived=False)
		expense_accs = ExpenseAccount.objects.filter(budget=b, is_archived=False)
		form_expense = FormExpenseNew(instance=ex)
		#(initial={'date_start': t_prev,'date_end': t_today})
		form_expense_item_new = FormExpenseItemNew(initial={'start_date': ex.payment_date,'end_date': ex.payment_date})
		items = ExpenseItem.objects.filter(expense=ex)
		recs = JournalRecord.objects.filter(event=ex)
		recs = recs.extra(order_by = ['-date', 'account__name'])
		return render(request, 'budget/expense_edit.html', {'budget': b, 'money_accs': money_accs, 'form_expense': form_expense, 'items': items, 'ex': ex, 'form_expense_item_new': form_expense_item_new, 'expense_accs': expense_accs, 'records': recs})
	return HttpResponseRedirect("/budget/")

@login_required
def expense_save(request, budget_id, expense_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		ex = Expense.objects.get(pk=expense_id)
		if (ex.budget != b):
			return HttpResponseRedirect("/budget/")
		ex.is_saved = True
		ex.save()
		return HttpResponseRedirect("/budget/" + str(b.id) + "/expense/" + str(ex.id) + "/")
	return HttpResponseRedirect("/budget/")
	
@login_required
def expense_item_edit(request, budget_id, expense_id, expense_item_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormExpenseItemNew(request.POST)
			if f.is_valid():
				try:
					e = f.save(commit=False)
					e.budget = b
					a = ExpenseAccount.objects.get(pk=request.POST['expense_acc_id'])
					e.expense_account = a
					
					i = ExpenseItem.objects.get(pk=expense_item_id)
					i.expense_account = e.expense_account
					i.amount = e.amount
					i.comment = e.comment
					i.start_date = e.start_date
					i.end_date = e.end_date
					
					if (i.expense.budget != b):
						return HttpResponseRedirect("/budget/")
					
					i.save()
					if i.expense.is_saved:
						return HttpResponseRedirect("/budget/" + str(b.id) + "/expense/" + str(i.expense.id) + "/save/")
					
					return HttpResponseRedirect("/budget/" + str(b.id) + "/expense/" + str(i.expense.id) + "/")
				except:
					pass
		
		i = ExpenseItem.objects.get(pk=expense_item_id)
		expense_accs = ExpenseAccount.objects.filter(budget=b, is_archived=False)
		form_expense_item_edit = FormExpenseItemNew(instance=i)
		return render(request, 'budget/expense_item_edit.html', {'budget': b, 'form_expense_item_edit': form_expense_item_edit, 'expense_accs': expense_accs, 'item': i})
	return HttpResponseRedirect("/budget/")
	
@login_required
def income_new(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormIncomeNew(request.POST)
			if f.is_valid():
				#try:
				e = f.save(commit=False)
				e.budget = b
				m = MoneyAccount.objects.get(pk=request.POST['money_acc_id'])
				i = IncomeAccount.objects.get(pk=request.POST['income_acc_id'])
				e.money_account = m
				e.income_account = i
				e.save()
				return HttpResponseRedirect("/budget/" + str(b.id) + "/income/" + str(e.id) + "/")
				#except:
				#	pass
		money_accs = MoneyAccount.objects.filter(budget=b, is_archived=False)
		income_accs = IncomeAccount.objects.filter(budget=b, is_archived=False)
		form_income_new = FormIncomeNew
		items = Expense.objects.filter(budget=b)
		return render(request, 'budget/income_new.html', {'budget': b, 'money_accs': money_accs, 'form_income_new': form_income_new, 'income_accs': income_accs})
	return HttpResponseRedirect("/budget/")
	
@login_required
def income_edit(request, budget_id, income_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormIncomeNew(request.POST)
			if f.is_valid():
				#try:
				e = f.save(commit=False)
				e.budget = b
				m = MoneyAccount.objects.get(pk=request.POST['money_acc_id'])
				i = IncomeAccount.objects.get(pk=request.POST['income_acc_id'])
				e.money_account = m
				e.income_account = i
				
				inc = Income.objects.get(pk=income_id)
				if inc.budget != b:
					return HttpResponseRedirect("/budget/" + str(b.id) + "/")
				
				inc.income_account = e.income_account
				inc.money_account = e.money_account
				inc.amount = e.amount
				inc.payment_date = e.payment_date
				inc.start_date = e.start_date
				inc.end_date = e.end_date
				inc.save()
					
				return HttpResponseRedirect("/budget/" + str(b.id) + "/income/" + str(inc.id) + "/")
				#except:
				#	pass
		
		inc = Income.objects.get(pk=income_id)
		money_accs = MoneyAccount.objects.filter(budget=b, is_archived=False)
		income_accs = IncomeAccount.objects.filter(budget=b, is_archived=False)
		recs = JournalRecord.objects.filter(event=inc)
		recs = recs.extra(order_by = ['-date', 'account__name'])
		form_income = FormIncomeNew(instance=inc)
		return render(request, 'budget/income_edit.html', {'budget': b, 'money_accs': money_accs, 'form_income': form_income, 'income_accs': income_accs, 'inc': inc, 'records': recs})
	return HttpResponseRedirect("/budget/")
	
@login_required
def transfer_new(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormMoneyTransferNew(request.POST)
			if f.is_valid():
				#try:
				e = f.save(commit=False)
				e.budget = b
				m_from = MoneyAccount.objects.get(pk=request.POST['money_acc_from_id'])
				m_to = MoneyAccount.objects.get(pk=request.POST['money_acc_to_id'])
				e.acc_from = m_from
				e.acc_to = m_to
				e.save()
				return HttpResponseRedirect("/budget/" + str(b.id) + "/transfer/" + str(e.id) + "/")
				#except:
				#	pass
		money_accs = MoneyAccount.objects.filter(budget=b, is_archived=False)
		form_transfer_new = FormMoneyTransferNew
		items = Expense.objects.filter(budget=b)
		return render(request, 'budget/transfer_new.html', { 'budget': b, 'money_accs': money_accs, 'form_transfer_new': form_transfer_new })
	return HttpResponseRedirect("/budget/")
	
@login_required
def transfer_edit(request, budget_id, transfer_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			f = FormMoneyTransferNew(request.POST)
			if f.is_valid():
				#try:
				e = f.save(commit=False)
				e.budget = b
				m_from = MoneyAccount.objects.get(pk=request.POST['money_acc_from_id'])
				m_to = MoneyAccount.objects.get(pk=request.POST['money_acc_to_id'])
				e.acc_from = m_from
				e.acc_to = m_to
				
				tr = MoneyTransfer.objects.get(pk=transfer_id)
				if tr.budget != b:
					return HttpResponseRedirect("/budget/" + str(b.id) + "/")
				
				tr.acc_from = e.acc_from
				tr.acc_to = e.acc_to
				tr.amount = e.amount
				tr.payment_date = e.payment_date
				tr.save()
					
				return HttpResponseRedirect("/budget/" + str(b.id) + "/transfer/" + str(tr.id) + "/")
				#except:
				#	pass
		tr = MoneyTransfer.objects.get(pk=transfer_id)
		money_accs = MoneyAccount.objects.filter(budget=b, is_archived=False)
		recs = JournalRecord.objects.filter(event=tr)
		recs = recs.extra(order_by = ['-date', 'account__name'])
		form_transfer_edit = FormMoneyTransferNew(instance=tr)
		return render(request, 'budget/transfer_edit.html', {'budget': b, 'money_accs': money_accs, 'form_transfer_edit': form_transfer_edit, 'tr': tr, 'records': recs})
	return HttpResponseRedirect("/budget/")
	
@login_required
def money_account_edit(request, budget_id, acc_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if bu.count() == 1:
		if request.method == "POST":
			if request.POST['form_id'] == "acc":
				f = FormAccMoneyNew(request.POST)
				if f.is_valid():
					e = f.save(commit=False)
					e.budget = b
					c = FinancialAccountCategory.objects.get(pk=request.POST['cat_id'])
					bnk = Bank.objects.get(pk=request.POST['bank_id'])
					e.category = c
					e.bank = bnk
					m_acc = MoneyAccount.objects.get(pk=acc_id)
					if m_acc.budget != b:
						return HttpResponseRedirect("/budget/" + str(b.id) + "/")
					
					m_acc.category = e.category
					m_acc.bank = e.bank
					m_acc.name = e.name
					m_acc.save()
						
					return HttpResponseRedirect("/budget/" + str(b.id) + "/accounts/money/" + str(m_acc.id) + "/")
					
			if request.POST['form_id'] == "init_balance":
				m_acc = MoneyAccount.objects.get(pk=acc_id)
				if m_acc.budget != b:
					return HttpResponseRedirect("/budget/" + str(b.id) + "/")
				f = FormInitBalance(request.POST)
				if f.is_valid():
					events_init = InitialBalance.objects.filter(account=m_acc)
					events_init.delete()
					
					e = f.save(commit=False)
					e.budget = b
					e.account = m_acc
					e.save()
					
					return HttpResponseRedirect("/budget/" + str(b.id) + "/accounts/money/" + str(m_acc.id) + "/")
					
		m_acc = MoneyAccount.objects.get(pk=acc_id)
		cat = FinancialAccountCategory.objects.filter(budget=b)
		banks = Bank.objects.filter(budget=b)
		form_acc_money = FormAccMoneyNew(instance=m_acc)
		form_init_balance = FormInitBalance
		recs = []
		if InitialBalance.objects.filter(account=m_acc).count():
			event_init = InitialBalance.objects.filter(account=m_acc)[0]
			recs = JournalRecord.objects.filter(event=event_init)
			form_init_balance = FormInitBalance(instance=event_init)
			
		all_records = JournalRecord.objects.filter(account=m_acc).order_by('-date')
		#all_records = sorted(all_records, key=lambda x: x.date, reverse=True)
		#all_records.sort(key=lambda x: x.date, reverse=True)
		
		return render(request, 'budget/money_account_edit.html', { 'budget': b, 'form_acc_money': form_acc_money, 'cat': cat, 'banks': banks, 'm_acc': m_acc, 'records': recs, 'form_init_balance':form_init_balance, 'all_records': all_records })
	return HttpResponseRedirect("/budget/")
	
@login_required
def report_profit(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if BudgetUser.objects.filter(budget=b, user=request.user).count():
		if request.method == "POST":
			f = FormReportProfitSetup(request.POST)
			if f.is_valid():
				t0 = f.cleaned_data['date_start']
				t1 = f.cleaned_data['date_end']
				rep = ReportIncome(t0, t1, b)
				rep_data_income = rep.get_lines_income()
				rep_data_expense = rep.get_lines_expense()
				report_ready = True
				return render(request, 'budget/report_profit.html', {'budget': b, 'form_setup':f, 'report_ready': report_ready, 'rep_data_income': rep_data_income, 'rep_data_expense': rep_data_expense })
			else:
				form_setup = FormReportProfitSetup
				report_ready = False
				return render(request, 'budget/report_profit.html', {'budget': b, 'form_setup':form_setup, 'report_ready': report_ready})
		else:
			t_today = date.today()
			dt = timedelta(days=30)
			t_prev = t_today - dt
			form_setup = FormReportProfitSetup(initial={'date_start': t_prev,'date_end': t_today})
			report_ready = False
			return render(request, 'budget/report_profit.html', {'budget': b, 'form_setup':form_setup, 'report_ready': report_ready})
	return HttpResponseRedirect("/budget/")
	
@login_required
def report_balance(request, budget_id):
	b = Budget.objects.get(pk=budget_id)
	bu = BudgetUser.objects.filter(budget=b, user=request.user)
	if BudgetUser.objects.filter(budget=b, user=request.user).count():
		if request.method == "POST":
			f = FormReportBalanceSetup(request.POST)
			if f.is_valid():
				t = f.cleaned_data['date_end']
				rep = ReportBalance(t, b)
				rep_data_money = rep.get_lines_money()
				rep_data_not_money = rep.get_lines_other()
				#rep_data_not_money = []
				report_ready = True
				return render(request, 'budget/report_balance.html', {'budget': b, 'form_setup':f, 'report_ready': report_ready, 'rep_data_money': rep_data_money, 'rep_data_not_money': rep_data_not_money })
			else:
				t_today = date.today()
				form_setup = FormReportBalanceSetup(initial={ 'date_end': t_today })
				report_ready = False
				return render(request, 'budget/report_balance.html', {'budget': b, 'form_setup':form_setup, 'report_ready': report_ready})
		else:
			t_today = date.today()
			form_setup = FormReportBalanceSetup(initial={ 'date_end': t_today })
			report_ready = False
			return render(request, 'budget/report_balance.html', {'budget': b, 'form_setup':form_setup, 'report_ready': report_ready})
	return HttpResponseRedirect("/budget/")
	
@login_required
def asset_account_edit(request, budget_id, acc_id):
	b = Budget.objects.get(pk=budget_id)
	if BudgetUser.objects.filter(budget=b, user=request.user).count():
		if request.method == "POST":
			if request.POST['form_id'] == "acc":
				f = FormAccAssetNew(request.POST)
				if f.is_valid():
					e = f.save(commit=False)
					e.budget = b
					m_acc = AssetAccount.objects.get(pk=acc_id)
					if m_acc.budget != b:
						return HttpResponseRedirect("/budget/" + str(b.id) + "/")
					
					m_acc.name = e.name
					m_acc.save()
						
					return HttpResponseRedirect("/budget/" + str(b.id) + "/accounts/asset/" + str(m_acc.id) + "/")
					
			if request.POST['form_id'] == "init_balance":
				m_acc = AssetAccount.objects.get(pk=acc_id)
				if m_acc.budget != b:
					return HttpResponseRedirect("/budget/" + str(b.id) + "/")
				f = FormInitBalance(request.POST)
				if f.is_valid():
					events_init = InitialBalance.objects.filter(account=m_acc)
					events_init.delete()
					
					e = f.save(commit=False)
					e.budget = b
					e.account = m_acc
					e.save()
					
					return HttpResponseRedirect("/budget/" + str(b.id) + "/accounts/asset/" + str(m_acc.id) + "/")
		
		m_acc = AssetAccount.objects.get(pk=acc_id)
		if m_acc.budget != b:
			return HttpResponseRedirect("/budget/" + str(b.id) + "/asset/")
		
		form_acc = FormAccAssetNew(instance=m_acc)
		form_init_balance = FormInitBalance
		recs = []
		if InitialBalance.objects.filter(account=m_acc).count():
			event_init = InitialBalance.objects.get(account=m_acc)
			recs = JournalRecord.objects.filter(event=event_init)
			form_init_balance = FormInitBalance(instance=event_init)
		
		return render(request, 'budget/asset_account_edit.html', {'budget': b, 'form_acc': form_acc, 'm_acc': m_acc, 'form_init_balance': form_init_balance, 'records': recs})
	return HttpResponseRedirect("/budget/")
	
@login_required
def liability_account_edit(request, budget_id, acc_id):
	b = Budget.objects.get(pk=budget_id)
	if BudgetUser.objects.filter(budget=b, user=request.user).count():
		if request.method == "POST":
			if request.POST['form_id'] == "acc":
				f = FormAccLiabilityNew(request.POST)
				if f.is_valid():
					e = f.save(commit=False)
					e.budget = b
					m_acc = LiabilityAccount.objects.get(pk=acc_id)
					if m_acc.budget != b:
						return HttpResponseRedirect("/budget/" + str(b.id) + "/")
					
					m_acc.name = e.name
					m_acc.save()
						
					return HttpResponseRedirect("/budget/" + str(b.id) + "/accounts/liability/" + str(m_acc.id) + "/")
					
			if request.POST['form_id'] == "init_balance":
				m_acc = LiabilityAccount.objects.get(pk=acc_id)
				if m_acc.budget != b:
					return HttpResponseRedirect("/budget/" + str(b.id) + "/")
				f = FormInitBalance(request.POST)
				if f.is_valid():
					events_init = InitialBalance.objects.filter(account=m_acc)
					events_init.delete()
					
					e = f.save(commit=False)
					e.budget = b
					e.account = m_acc
					e.save()
					
					return HttpResponseRedirect("/budget/" + str(b.id) + "/accounts/liability/" + str(m_acc.id) + "/")
		
		m_acc = LiabilityAccount.objects.get(pk=acc_id)
		if m_acc.budget != b:
			return HttpResponseRedirect("/budget/" + str(b.id) + "/liability/")
		
		form_acc = FormAccLiabilityNew(instance=m_acc)
		form_init_balance = FormInitBalance
		recs = []
		if InitialBalance.objects.filter(account=m_acc).count():
			event_init = InitialBalance.objects.get(account=m_acc)
			recs = JournalRecord.objects.filter(event=event_init)
			form_init_balance = FormInitBalance(instance=event_init)
		
		return render(request, 'budget/liability_account_edit.html', {'budget': b, 'form_acc': form_acc, 'm_acc': m_acc, 'form_init_balance': form_init_balance, 'records': recs})
	return HttpResponseRedirect("/budget/")
	
@login_required
def asset_account_delete(request, budget_id, acc_id):
	b = Budget.objects.get(pk=budget_id)
	if BudgetUser.objects.filter(budget=b, user=request.user).count():
		m_acc = AssetAccount.objects.get(pk=acc_id)
		if m_acc.budget != b:
			return HttpResponseRedirect("/budget/" + str(b.id) + "/accounts/asset/")
		
		m_acc.is_archived = True
		m_acc.save()
		return HttpResponseRedirect("/budget/" + str(b.id) + "/accounts/asset/")
	return HttpResponseRedirect("/budget/")
	
@login_required
def liability_account_delete(request, budget_id, acc_id):
	b = Budget.objects.get(pk=budget_id)
	if BudgetUser.objects.filter(budget=b, user=request.user).count():
		m_acc = LiabilityAccount.objects.get(pk=acc_id)
		if m_acc.budget != b:
			return HttpResponseRedirect("/budget/" + str(b.id) + "/accounts/liability/")
		
		m_acc.is_archived = True
		m_acc.save()
		return HttpResponseRedirect("/budget/" + str(b.id) + "/accounts/liability/")
	return HttpResponseRedirect("/budget/")