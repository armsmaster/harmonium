from django.conf.urls import url

from . import views

app_name = 'budget'

urlpatterns = [
    url(r'^$', views.index, name='index'),
	url(r'^all/$', views.budget_all, name='budget_all'),
	url(r'^(?P<budget_id>[0-9]+)/$', views.budget, name='budget'),
	url(r'^(?P<budget_id>[0-9]+)/edit/$', views.budget_edit, name='budget_edit'),
	url(r'^(?P<budget_id>[0-9]+)/cat-expenses/$', views.cat_expenses, name='cat_expenses'),
	url(r'^(?P<budget_id>[0-9]+)/cat-income/$', views.cat_income, name='cat_income'),
	url(r'^(?P<budget_id>[0-9]+)/cat-fin-account/$', views.cat_fin_account, name='cat_fin_account'),
	url(r'^(?P<budget_id>[0-9]+)/banks/$', views.banks, name='banks'),
	url(r'^(?P<budget_id>[0-9]+)/accounts/expense/$', views.acc_expense, name='acc_expense'),
	url(r'^(?P<budget_id>[0-9]+)/accounts/income/$', views.acc_income, name='acc_income'),
	url(r'^(?P<budget_id>[0-9]+)/accounts/money/$', views.acc_money, name='acc_money'),
	url(r'^(?P<budget_id>[0-9]+)/accounts/money/(?P<acc_id>[0-9]+)/$', views.money_account_edit, name='money_account_edit'),
	url(r'^(?P<budget_id>[0-9]+)/accounts/asset/$', views.acc_asset, name='acc_asset'),
	url(r'^(?P<budget_id>[0-9]+)/accounts/liability/$', views.acc_liability, name='acc_liability'),
	url(r'^(?P<budget_id>[0-9]+)/expense/new/$', views.expense_new, name='expense_new'),
	url(r'^expense/new/$', views.expense_new_aux, name='expense_new_aux'),
	url(r'^income/new/$', views.income_new_aux, name='income_new_aux'),
	url(r'^(?P<budget_id>[0-9]+)/expense/$', views.expenses, name='expenses'),
	url(r'^(?P<budget_id>[0-9]+)/expense/(?P<expense_id>[0-9]+)/$', views.expense_edit, name='expense_edit'),
	url(r'^(?P<budget_id>[0-9]+)/expense/(?P<expense_id>[0-9]+)/save/$', views.expense_save, name='expense_save'),
	url(r'^(?P<budget_id>[0-9]+)/expense/(?P<expense_id>[0-9]+)/items/(?P<expense_item_id>[0-9]+)/$', views.expense_item_edit, name='expense_item_edit'),
	url(r'^(?P<budget_id>[0-9]+)/income/new/$', views.income_new, name='income_new'),
	url(r'^(?P<budget_id>[0-9]+)/transfer/new/$', views.transfer_new, name='transfer_new'),
	url(r'^(?P<budget_id>[0-9]+)/transfer/(?P<transfer_id>[0-9]+)/$', views.transfer_edit, name='transfer_edit'),
	url(r'^(?P<budget_id>[0-9]+)/transfer/$', views.money_transfers, name='money_transfers'),
	url(r'^(?P<budget_id>[0-9]+)/income/(?P<income_id>[0-9]+)/$', views.income_edit, name='income_edit'),
	url(r'^(?P<budget_id>[0-9]+)/income/$', views.incomes, name='incomes'),
	url(r'^(?P<budget_id>[0-9]+)/report/profit/$', views.report_profit, name='report_profit'),
	url(r'^(?P<budget_id>[0-9]+)/report/balance/$', views.report_balance, name='report_balance'),
	url(r'^(?P<budget_id>[0-9]+)/accounts/asset/(?P<acc_id>[0-9]+)/$', views.asset_account_edit, name='asset_account_edit'),
	url(r'^(?P<budget_id>[0-9]+)/accounts/asset/(?P<acc_id>[0-9]+)/delete/$', views.asset_account_delete, name='asset_account_delete'),
	url(r'^(?P<budget_id>[0-9]+)/accounts/liability/(?P<acc_id>[0-9]+)/$', views.liability_account_edit, name='liability_account_edit'),
	url(r'^(?P<budget_id>[0-9]+)/accounts/liability/(?P<acc_id>[0-9]+)/delete/$', views.liability_account_delete, name='liability_account_delete'),
]