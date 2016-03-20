from django import forms
from django.forms import widgets

from .models import Budget, BudgetUser
from .models import ExpenseCategory, IncomeCategory, FinancialAccountCategory, Bank
from .models import Acc, ExpenseAccount, MoneyAccount, IncomeAccount, AssetAccount, LiabilityAccount
from .models import Expense, ExpenseItem, MoneyTransfer, Income, JournalRecord, InitialBalance

MIN_YEAR = 2015
MAX_YEAR = 2025

class FormBudgetNew(forms.ModelForm):
	class Meta:
		model = Budget
		fields = ('name',)
		
class FormBudgetUser(forms.Form):
	user_name = forms.CharField(label='User Name', max_length=100)

class FormCatExpenseNew(forms.ModelForm):
	class Meta:
		model = ExpenseCategory
		fields = ('name',)
		
class FormCatIncomeNew(forms.ModelForm):
	class Meta:
		model = IncomeCategory
		fields = ('name',)
		
class FormCatFinAccountNew(forms.ModelForm):
	class Meta:
		model = FinancialAccountCategory
		fields = ('name',)
		
class FormBankNew(forms.ModelForm):
	class Meta:
		model = Bank
		fields = ('name',)
		
class FormAccExpenseNew(forms.ModelForm):
	class Meta:
		model = ExpenseAccount
		fields = ('name',)

class FormAccIncomeNew(forms.ModelForm):
	class Meta:
		model = IncomeAccount
		fields = ('name',)
		
class FormAccMoneyNew(forms.ModelForm):
	class Meta:
		model = MoneyAccount
		fields = ('name',)
		
class FormAccAssetNew(forms.ModelForm):
	class Meta:
		model = AssetAccount
		fields = ('name',)
		
class FormAccLiabilityNew(forms.ModelForm):
	class Meta:
		model = LiabilityAccount
		fields = ('name',)
		
class FormExpenseNew(forms.ModelForm):
	class Meta:
		model = Expense
		fields = ('shop_name','payment_date','comment',)
		widgets = { 'payment_date': forms.SelectDateWidget(years=range(MIN_YEAR, MAX_YEAR)), }
		labels = {'shop_name': ('Counterparty'),}
		
class FormExpenseItemNew(forms.ModelForm):
	class Meta:
		model = ExpenseItem
		fields = ('amount','start_date','end_date','comment',)
		widgets = { 'start_date': forms.SelectDateWidget(years=range(MIN_YEAR, MAX_YEAR)), 'end_date': forms.SelectDateWidget(years=range(MIN_YEAR, MAX_YEAR)), }
		
class FormIncomeNew(forms.ModelForm):
	class Meta:
		model = Income
		fields = ('amount', 'payment_date', 'start_date', 'end_date',)
		widgets = { 'start_date': forms.SelectDateWidget(years=range(MIN_YEAR, MAX_YEAR)), 'end_date': forms.SelectDateWidget(years=range(MIN_YEAR, MAX_YEAR)), 'payment_date': forms.SelectDateWidget(years=range(MIN_YEAR, MAX_YEAR)), }
		
class FormMoneyTransferNew(forms.ModelForm):
	class Meta:
		model = MoneyTransfer
		fields = ('comment', 'amount', 'payment_date',)
		widgets = { 'payment_date': forms.SelectDateWidget(years=range(MIN_YEAR, MAX_YEAR)), }
		
class FormInitBalance(forms.ModelForm):
	class Meta:
		model = InitialBalance
		fields = ('date', 'amount', )
		widgets = { 'date': forms.SelectDateWidget(years=range(MIN_YEAR, MAX_YEAR)), }
		
class FormReportProfitSetup(forms.Form):
	date_start = forms.DateField(widget=forms.SelectDateWidget(years=range(MIN_YEAR, MAX_YEAR)), label='Date Start')
	date_end = forms.DateField(widget=forms.SelectDateWidget(years=range(MIN_YEAR, MAX_YEAR)))
	
class FormReportBalanceSetup(forms.Form):
	date_end = forms.DateField(widget=forms.SelectDateWidget(years=range(MIN_YEAR, MAX_YEAR)), label='Report Date')