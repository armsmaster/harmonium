from django.db import models
from django.db.models import Count, Min, Sum, Avg

from datetime import datetime
from datetime import date
from datetime import timedelta

# Create your models here.
class Budget(models.Model):
	name = models.CharField(max_length=200)
	user_owner = models.ForeignKey('auth.User')
	def save(self):
		super(Budget, self).save()
		existing_bu = BudgetUser.objects.filter(user=self.user_owner, budget=self)
		if existing_bu.count() == 0:
			bu = BudgetUser(budget=self, user=self.user_owner)
			bu.save()
			existing_bu = BudgetUser.objects.filter(user=self.user_owner)
			if existing_bu.count() == 1:
				bu.is_main = True
				bu.save()

class BudgetUser(models.Model):
	budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
	user = models.ForeignKey('auth.User')
	is_main = models.BooleanField(default=False)

#categories
class ExpenseCategory(models.Model):
	budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)

class IncomeCategory(models.Model):
	budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)

class FinancialAccountCategory(models.Model):
	budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)

class Bank(models.Model):
	budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)

#accounts - base
class Acc(models.Model):
	budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)
	is_archived = models.BooleanField(default=False)

#accounts - derived		
class ExpenseAccount(Acc):
	category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)

class MoneyAccount(Acc):
	category = models.ForeignKey(FinancialAccountCategory, on_delete=models.CASCADE)
	bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
	
class IncomeAccount(Acc):
	category = models.ForeignKey(IncomeCategory, on_delete=models.CASCADE)
	
class AssetAccount(Acc):
	pass
	
class LiabilityAccount(Acc):
	pass

#business events
class EventBase(models.Model):
	budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
	comment = models.CharField(max_length=200, default='', null=True, blank=True)
	
class Expense(EventBase):
	payment_date = models.DateField(default=date.today)
	money_account = models.ForeignKey(MoneyAccount, on_delete=models.CASCADE)
	shop_name = models.CharField(max_length=200, default='', null=True, blank=True)
	is_saved = models.BooleanField(default=False)
	
	def amount(self):
		items = ExpenseItem.objects.filter(expense=self)
		amt = 0
		for i in items:
			amt += i.amount
		return amt
	
	def average(self):
		items = ExpenseItem.objects.filter(expense=self)
		amt = 0
		for i in items:
			amt += i.average()
		return amt
	
	def save(self):
		super(Expense, self).save()
		if self.is_saved == True:
			jrs = JournalRecord.objects.filter(event=self)
			jrs.delete()
			total_amt = 0
			eis = ExpenseItem.objects.filter(expense=self)
			all_recs = []
			for i in eis:
				recs = i.generate_journal_records()
				all_recs += recs
				total_amt += i.amount
				
			cmnt = self.comment
			
			if cmnt == '':
				cmnt = self.shop_name
			else:
				cmnt = cmnt + ' @' + self.shop_name
			
			jr = JournalRecord(budget=self.budget, event=self, date=self.payment_date, account=self.money_account, amount=-total_amt, comment=cmnt, event_type='expense')
			all_recs.append(jr)
			JournalRecord.objects.bulk_create(all_recs)
	
class ExpenseItem(models.Model):
	expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
	expense_account = models.ForeignKey(ExpenseAccount, on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=16, decimal_places=4)
	start_date = models.DateField(default=date.today)
	end_date = models.DateField(default=date.today)
	comment = models.CharField(max_length=200, default='', null=True, blank=True)
	
	def average(self):
		delta = self.end_date - self.start_date
		d = delta.days + 1
		return round(self.amount / d, 1)
	
	def avg(self):
		delta = self.end_date - self.start_date
		d = delta.days + 1
		return round(self.amount / d, 8)
	
	def generate_journal_records(self):
		t = self.start_date
		dt = timedelta(days=1)
		records = []
		
		prepaid_expenses_accs = AssetAccount.objects.filter(name="PREPAID_EXPENSES")
		if prepaid_expenses_accs.count() == 0:
			prepaid_expenses_acc = AssetAccount(name="PREPAID_EXPENSES", budget=self.expense.budget)
			prepaid_expenses_acc.save()
		else:
			prepaid_expenses_acc = prepaid_expenses_accs[0]
		
		accs_payable = LiabilityAccount.objects.filter(name="ACCOUNTS_PAYABLE")
		if accs_payable.count() == 0:
			acc_payable = LiabilityAccount(name="ACCOUNTS_PAYABLE", budget=self.expense.budget)
			acc_payable.save()
		else:
			acc_payable = accs_payable[0]
		
		money_acc = self.expense.money_account
		
		payable = 0
		prepaid = 0
		
		while t <= self.end_date:
			cmnt = ''
			if self.comment != '':
				cmnt = self.comment + ' @' + self.expense.shop_name
				
			if cmnt == '':
				if self.expense.comment != '':
					cmnt = self.expense.comment + ' @' + self.expense.shop_name
					
			if cmnt == '':
				if self.expense.shop_name != '':
					cmnt = self.expense.shop_name
			
			j = JournalRecord(budget=self.expense.budget, event=self.expense, date=t, account=self.expense_account, amount=self.avg(), comment=cmnt, event_type='expense')
			records.append(j)
			
			if t < self.expense.payment_date:
				j = JournalRecord(budget=self.expense.budget, event=self.expense, date=t, account=acc_payable, amount=-self.avg(), comment=cmnt, event_type='expense')
				records.append(j)
			elif t > self.expense.payment_date:
				j = JournalRecord(budget=self.expense.budget, event=self.expense, date=t, account=prepaid_expenses_acc, amount=-self.avg(), comment=cmnt, event_type='expense')
				records.append(j)
			elif t == self.expense.payment_date:
				pass
				#j = JournalRecord(budget=self.expense.budget, event=self.expense, date=t, account=money_acc, amount=-self.avg(), event_type='expense')
				#records.append(j)
			
			t += dt
		
		delta = self.end_date - self.start_date
		days_total = delta.days
		
		delta = self.end_date - self.expense.payment_date
		days_prepaid = min(max(delta.days, 0), days_total)
		
		delta = self.expense.payment_date - self.start_date
		days_payable = min(max(delta.days, 0), days_total)
			
		payable = days_payable * self.avg()
		prepaid = days_prepaid * self.avg()
		
		if self.expense.payment_date > self.end_date:
			payable += self.avg()
		
		if self.expense.payment_date < self.start_date:
			prepaid += self.avg()
		
		if days_prepaid > 0:
			#j = JournalRecord(budget=self.expense.budget, event=self.expense, date=self.expense.payment_date, account=money_acc, amount=-prepaid)
			#records.append(j)
			j = JournalRecord(budget=self.expense.budget, event=self.expense, date=self.expense.payment_date, account=prepaid_expenses_acc, amount=prepaid, comment=cmnt, event_type='expense')
			records.append(j)
		
		if days_payable > 0:
			#j = JournalRecord(budget=self.expense.budget, event=self.expense, date=self.expense.payment_date, account=money_acc, amount=-payable)
			#records.append(j)
			j = JournalRecord(budget=self.expense.budget, event=self.expense, date=self.expense.payment_date, account=acc_payable, amount=payable, comment=cmnt, event_type='expense')
			records.append(j)
			
		return records
		
class MoneyTransfer(EventBase):
	payment_date = models.DateField(default=date.today)
	acc_from = models.ForeignKey(MoneyAccount, on_delete=models.CASCADE, related_name='transfers_outgoing')
	acc_to = models.ForeignKey(MoneyAccount, on_delete=models.CASCADE, related_name='transfers_incoming')
	amount = models.DecimalField(max_digits=16, decimal_places=4)
	
	def save(self):
		super(MoneyTransfer, self).save()
		jrs = JournalRecord.objects.filter(event=self)
		jrs.delete()
		
		j1 = JournalRecord(budget=self.budget, event=self, date=self.payment_date, account=self.acc_to, amount=self.amount, comment='[FROM] '+self.acc_from.name, event_type='transfer')
		j2 = JournalRecord(budget=self.budget, event=self, date=self.payment_date, account=self.acc_from, amount=-self.amount, comment='[TO] '+self.acc_to.name, event_type='transfer')
		records = [j1, j2]
		JournalRecord.objects.bulk_create(records)
		
class InitialBalance(EventBase):
	account = models.ForeignKey(Acc, on_delete=models.CASCADE)
	date = models.DateField(default=date.today)
	amount = models.DecimalField(max_digits=16, decimal_places=4)
	
	def save(self):
		super(InitialBalance, self).save()
		j = JournalRecord(budget=self.budget, event=self, date=self.date, account=self.account, amount=self.amount, comment='[INITIAL] '+ self.comment)
		j.save()
		
class Income(EventBase):
	payment_date = models.DateField(default=date.today)
	money_account = models.ForeignKey(MoneyAccount, on_delete=models.CASCADE)
	income_account = models.ForeignKey(IncomeAccount, on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=16, decimal_places=4)
	start_date = models.DateField(default=date.today)
	end_date = models.DateField(default=date.today)
	
	def average(self):
		delta = self.end_date - self.start_date
		d = delta.days + 1
		return round(self.amount / d, 1)
	
	def avg(self):
		delta = self.end_date - self.start_date
		d = delta.days + 1
		return round(self.amount / d, 8)
		
	def save(self):
		super(Income, self).save()
		
		jrs = JournalRecord.objects.filter(event=self)
		jrs.delete()
		
		t = self.start_date
		dt = timedelta(days=1)
		records = []
		
		ar_accs = AssetAccount.objects.filter(name="ACCOUNTS_RECEIVABLE")
		if ar_accs.count() == 0:
			ar_acc = AssetAccount(name="ACCOUNTS_RECEIVABLE", budget=self.budget)
			ar_acc.save()
		else:
			ar_acc = ar_accs[0]
		
		adv_accs = LiabilityAccount.objects.filter(name="ADVANCES_RECEIVED")
		if adv_accs.count() == 0:
			adv_acc = LiabilityAccount(name="ADVANCES_RECEIVED", budget=self.budget)
			adv_acc.save()
		else:
			adv_acc = adv_accs[0]
		
		money_acc = self.money_account
		income_acc = self.income_account
		
		while t <= self.end_date:
			
			j = JournalRecord(budget=self.budget, event=self, date=t, account=income_acc, amount=-self.avg(), event_type='income')
			records.append(j)
			
			if t < self.payment_date:
				j = JournalRecord(budget=self.budget, event=self, date=t, account=ar_acc, amount=self.avg(), comment=income_acc.name, event_type='income')
				records.append(j)
			elif t > self.payment_date:
				j = JournalRecord(budget=self.budget, event=self, date=t, account=adv_acc, amount=self.avg(), comment=income_acc.name, event_type='income')
				records.append(j)
			elif t == self.payment_date:
				pass
			
			t += dt
		
		delta = self.end_date - self.start_date
		days_total = delta.days
		
		delta = self.end_date - self.payment_date
		days_adv = min(max(delta.days, 0), days_total)
		
		delta = self.payment_date - self.start_date
		days_ar = min(max(delta.days, 0), days_total)
			
		ar = days_ar * self.avg()
		adv = days_adv * self.avg()
		
		if self.payment_date > self.end_date:
			ar += self.avg()
			days_ar += 1
		
		if self.payment_date < self.start_date:
			adv += self.avg()
			days_adv += 1
		
		if days_ar > 0:
			j = JournalRecord(budget=self.budget, event=self, date=self.payment_date, account=ar_acc, amount=-ar, comment=income_acc.name, event_type='income')
			records.append(j)
		
		if days_adv > 0:
			j = JournalRecord(budget=self.budget, event=self, date=self.payment_date, account=adv_acc, amount=-adv, comment=income_acc.name, event_type='income')
			records.append(j)
			
		j = JournalRecord(budget=self.budget, event=self, date=self.payment_date, account=self.money_account, amount=self.amount, comment=income_acc.name, event_type='income')
		records.append(j)
		
		JournalRecord.objects.bulk_create(records)
	
class JournalRecord(models.Model):
	budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
	event = models.ForeignKey(EventBase, on_delete=models.CASCADE)
	event_type = models.CharField(max_length=200, default='', null=True, blank=True)
	date = models.DateField(default=date.today)
	account = models.ForeignKey(Acc, on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=16, decimal_places=4)
	comment = models.CharField(max_length=200, default='', null=True, blank=True)
	
class ReportLine(object):
	def __init__(self, n_tabs, string_line, amount, share_weight):
		self.prefix = str('....' * n_tabs)
		self.string_line = string_line
		self.amount = round(amount, 2)
		self.share_weight = share_weight
		
class ReportGroupLines(object):
	def __init__(self, main_line, id):
		self.main_line = main_line
		self.id = id
		self.details = []
		
	def add_item(self, itm):
		self.details.append(itm)
		
	def sort_amount(self):
		self.details = sorted(self.details, key=lambda x: x.main_line.amount, reverse=True)
	
	def sort_string(self):
		self.details = sorted(self.details, key=lambda x: x.main_line.string_line, reverse=True)
		
	def count(self):
		return self.details.count()
		
class ReportIncome(object):
	def __init__(self, date_start, date_end, budget):
		self.date_start = date_start
		self.date_end = date_end
		self.budget = budget
		
	def get_lines_income(self):
		income_cats = IncomeCategory.objects.filter(budget=self.budget)
		income_line = ReportLine(0, '[TOTAL INCOME]',0,100)
		income_group = ReportGroupLines(income_line, 0)
		for x in income_cats:
			cat_sum = 0
			cat_line = ReportLine(1, x.name,0,0)
			cat_group = ReportGroupLines(cat_line, x.id)
			accs = IncomeAccount.objects.filter(category=x)
			for a in accs:
				acc_sum = 0
				acc_line = ReportLine(2, a.name,0,0)
				acc_group = ReportGroupLines(acc_line, a.id)
				
				recs = JournalRecord.objects.filter(account=a, date__lte=self.date_end, date__gte=self.date_start)
				recs_agg = recs.aggregate(r_sum=Sum('amount'))
				acc_sum = 0
				if recs_agg['r_sum']:
					acc_sum = -recs_agg['r_sum']
				acc_group.main_line.amount = acc_sum
				
				for r in recs:
					temp_amt = -r.amount
					temp_share = 0
					if acc_sum != 0:
						temp_share = round((-r.amount) / acc_sum * 100, 2)
					r_line = ReportLine(3, str(r.date) + r.comment,temp_amt,temp_share)
					r_group = ReportGroupLines(r_line, r.id)
					acc_group.add_item(r_group)
				
				acc_group.sort_string()
				cat_sum += acc_sum
				cat_group.add_item(acc_group)
				
			cat_group.main_line.amount = cat_sum
			cat_group.sort_amount()
			for i in cat_group.details:
				if cat_sum != 0:
					i.main_line.share_weight = round(i.main_line.amount / cat_sum * 100, 2)
			income_group.main_line.amount += cat_sum
			income_group.add_item(cat_group)
			income_group.sort_amount()
			
		for x in income_group.details:
			if income_group.main_line.amount != 0:
				x.main_line.share_weight = round(x.main_line.amount / income_group.main_line.amount * 100, 2)
		
		return income_group
		
	def get_lines_expense(self):
		expense_cats = ExpenseCategory.objects.filter(budget=self.budget)
		total_line = ReportLine(0, '[TOTAL EXPENSES]',0,100)
		total_group = ReportGroupLines(total_line, 0)
		for x in expense_cats:
			cat_sum = 0
			cat_line = ReportLine(1, x.name,0,0)
			cat_group = ReportGroupLines(cat_line, x.id)
			accs = ExpenseAccount.objects.filter(category=x)
			for a in accs:
				acc_sum = 0
				acc_line = ReportLine(2, a.name,0,0)
				acc_group = ReportGroupLines(acc_line, a.id)
				
				recs = JournalRecord.objects.filter(account=a, date__lte=self.date_end, date__gte=self.date_start)
				recs_agg = recs.aggregate(r_sum=Sum('amount'))
				acc_sum = 0
				if recs_agg['r_sum']:
					acc_sum = recs_agg['r_sum']
				acc_group.main_line.amount = acc_sum
				
				for r in recs:
					temp_amt = r.amount
					temp_share = 0
					if acc_sum != 0:
						try:
							temp_share = round(r.amount / acc_sum * 100, 2)
						except:
							pass
					r_line = ReportLine(3, str(r.date)+ ' ' + r.comment, temp_amt, temp_share)
					r_group = ReportGroupLines(r_line, r.id)
					acc_group.add_item(r_group)
					
				acc_group.sort_string()
				cat_sum += acc_sum
				cat_group.add_item(acc_group)
				cat_group.sort_amount()
				
			cat_group.main_line.amount = cat_sum
			for i in cat_group.details:
				if cat_sum != 0:
					i.main_line.share_weight = round(i.main_line.amount / cat_sum * 100, 2)
			total_group.main_line.amount += cat_sum
			total_group.add_item(cat_group)
			total_group.sort_amount()
			
		for x in total_group.details:
			if total_group.main_line.amount != 0:
				x.main_line.share_weight = round(x.main_line.amount / total_group.main_line.amount * 100, 2)
		
		return total_group
		
class ReportBalance(object):
	def __init__(self, date_end, budget):
		self.date_end = date_end
		self.budget = budget
		
	def get_lines_money(self):
		money_cats = FinancialAccountCategory.objects.filter(budget=self.budget)
		total_line = ReportLine(0, '[NET MONEY]', 0, 100)
		total_group = ReportGroupLines(total_line, 0)
		for x in money_cats:
			cat_sum = 0
			cat_line = ReportLine(1, x.name, 0, 0)
			cat_group = ReportGroupLines(cat_line, x.id)
			accs = MoneyAccount.objects.filter(category=x)
			for a in accs:
				acc_line = ReportLine(2, a.name,0,0)
				acc_group = ReportGroupLines(acc_line, a.id)
				
				recs = JournalRecord.objects.filter(account=a, date__lte=self.date_end)
				recs_agg = recs.aggregate(r_sum=Sum('amount'))
				
				if recs_agg['r_sum']:
					acc_group.main_line.amount = recs_agg['r_sum']
				
				cat_sum += acc_group.main_line.amount
				cat_group.add_item(acc_group)
				cat_group.sort_amount()
				
			cat_group.main_line.amount = cat_sum
			total_group.main_line.amount += cat_sum
			total_group.add_item(cat_group)
			
		total_group.sort_amount()
		return total_group
		
	def get_lines_other(self):
		total_line = ReportLine(0, '[NET OTHER A/L]', 0, 100)
		total_group = ReportGroupLines(total_line, 0)
		
		#other assets
		cat_sum = 0
		cat_line_assets = ReportLine(1, "[OTHER ASSETS]", 0, 0)
		cat_group_assets = ReportGroupLines(cat_line_assets, 'BALANCE_OTHER_ASSETS')
		accs = AssetAccount.objects.filter(budget=self.budget)
		for a in accs:
			acc_line = ReportLine(2, a.name, 0, 0)
			acc_group = ReportGroupLines(acc_line, a.id)
			
			recs = JournalRecord.objects.filter(account=a, date__lte=self.date_end)
			recs_agg = recs.aggregate(r_sum=Sum('amount'))
			
			if recs_agg['r_sum']:
				acc_group.main_line.amount = recs_agg['r_sum']
			
			cat_sum += acc_group.main_line.amount
			cat_group_assets.add_item(acc_group)
		
		cat_group_assets.sort_amount()
		cat_group_assets.main_line.amount = cat_sum
		total_group.main_line.amount += cat_sum
		total_group.add_item(cat_group_assets)
		
		#other liabilities
		cat_sum = 0
		cat_line_liab = ReportLine(1, "[OTHER LIABILITIES]", 0, 0)
		cat_group_liab = ReportGroupLines(cat_line_liab, 'BALANCE_OTHER_LIABILITIES')
		accs = LiabilityAccount.objects.filter(budget=self.budget)
		for a in accs:
			acc_line = ReportLine(2, a.name, 0, 0)
			acc_group = ReportGroupLines(acc_line, a.id)
			
			recs = JournalRecord.objects.filter(account=a, date__lte=self.date_end)
			recs_agg = recs.aggregate(r_sum=Sum('amount'))
			
			if recs_agg['r_sum']:
				acc_group.main_line.amount = recs_agg['r_sum']
			
			cat_sum += acc_group.main_line.amount
			cat_group_liab.add_item(acc_group)
		
		cat_group_liab.sort_amount()
		cat_group_liab.main_line.amount = cat_sum
		total_group.main_line.amount += cat_sum
		total_group.add_item(cat_group_liab)
		
		return total_group