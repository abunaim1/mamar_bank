from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import CreateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from . models import Transaction, UserBankAccount, BankCrupt
from .forms import DepositForm, WithdrawForm, TransferMoneyForm
from .constants import DEPOSIT, WITHDRAWAL, LOAN, LOAN_PAID, TRANSFER, RECEIVED
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string


def send_transaction_email(user, amount, mail_subject, template):
    message = render_to_string(template,{
        'user' : user,
        'amount' : amount
    })
    send_email = EmailMultiAlternatives(mail_subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html") 
    send_email.send()


# we use class based view, create view. 
#amra ei class take prottekbar inherit kore withdraw, loan, deposite sob gula kaj korbo
class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    model = Transaction
    template_name = 'transaction_from.html'
    title = ''
    success_url = reverse_lazy('transaction_report') # reverse_lazy use kori jokhn amra ei url theke oi url e jabo tokhn loading time komanor jonne. 

    # jokhon kono form create hobe sekhane ekta constructor call hobe setar moddhe ami ekta account use korchi jeta jei user login thakbe tar account, and sei account ta ami ekhan theke evabe pathai dilam.
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account' : self.request.user.account,
        })
        return kwargs
    
    # buit in vabe class e ekta context thake oitake override kortesi and update kortechi ekta title diya
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title' : self.title
        })
        return context

class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposite'

    def get_initial(self):
         initial = {'transaction_type' : DEPOSIT}
         return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount 
        account.save(
            update_fields = ['balance']
        )
        messages.success(self.request, f'{amount}$ is deposited successfully')

        send_transaction_email(self.request.user, amount, 'Deposite message', 'deposite_email.html')

        return super().form_valid(form)
    
class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw'

    def get_initial(self):
         initial = {'transaction_type' : WITHDRAWAL}
         return initial
    def form_valid(self, form):
        try:
            obj = BankCrupt.objects.get(is_bankcrupt=True)
            messages.warning(self.request,'BANKCRUPT!!!!') 
        except BankCrupt.DoesNotExist:
            amount = form.cleaned_data.get('amount')
            account = self.request.user.account
            account.balance -= amount 
            account.save(
                update_fields = ['balance']
            )
            messages.success(self.request, f'{amount}$ withdrawn successfully')
        
        send_transaction_email(self.request.user, amount, 'Withdrawal message', 'withdraw_email.html')

        return super().form_valid(form)
    
class LoanRequestView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Request For Loan'

    def get_initial(self):
         initial = {'transaction_type' : LOAN}
         return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transaction.objects.filter(account=self.request.user.account, transaction_type=LOAN, loan_approve=True).count()

        if current_loan_count>=3:
            return HttpResponse('You crossed the limitations for request')
        
        messages.success(self.request, f'Loan request {amount}$ send to your admin')

        send_transaction_email(self.request.user, amount, 'Request for a loan', 'loan_email.html')

        return super().form_valid(form)

#we are using ListView karon amader transaction report ta list akare dekhabe ekta.
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transaction_report.html'
    model = Transaction
    balance = 0
    #context_object_name = 'repost_list' #eitake dhore loop chaliye repost er sob information pawa jabe, othoba chaile object_list likheo pawa jabe, amra object_list use kortesi jeta build in.

    #report er moddhe date time onujai filter korte amra 'GET' request kori, and ei date gula url e chole jai and amra ekhan theke dhori otake. etkae query kora bole. or jonne ei method ta:
    def get_queryset(self):

        # jodi user kono rokom filter use na kore date time diye tahole ekhane user er all transaction report dekhabo
        queryset = super().get_queryset().filter(
            account = self.request.user.account
        )

        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)
             
            self.balance = Transaction.objects.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account' : self.request.user.account
        })
        return context

# ekhane ListVew othoba DetailsView er kono kaj nai, just user loan ta korbe so ei khane amra View take user korlam. 
class PayLoanView(LoginRequiredMixin,View ):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)

        if loan.loan_approve:
            user_account = loan.account
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type =LOAN_PAID
                loan.save()
                return redirect('loan_list')
            else:
                messages.error(self.request, f'Loan amount is grater than available balance')
                return redirect('loan_list')

class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'loan_request.html'
    context_object_name = 'loans'

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account = user_account, transaction_type =  LOAN)
        return queryset
    
class TransferBalance(LoginRequiredMixin, View):
    template_name = 'transfer_balance.html'
    success_url = reverse_lazy('transaction_report')

    def get(self, request):
        form = TransferMoneyForm()
        return render(request, self.template_name, {'form':form})
    
    def post(self, request):
        form = TransferMoneyForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            to_user_id = form.cleaned_data['to_user_id']
            current_user = self.request.user.account
            try:
                to_user = UserBankAccount.objects.get(account_no=to_user_id)
                if current_user.balance >= amount:  
                    current_user.balance -= amount  
                    to_user.balance += amount       
                    current_user.save()
                    to_user.save()
                    messages.success(self.request, 'Success!')
                else:
                    messages.error(self.request, 'Insufficient balance!')
            except UserBankAccount.DoesNotExist:
                messages.error(self.request, 'Acount number invalid!')

            Transaction.objects.create(
                account = current_user,
                amount = amount,
                balance_after_transaction = current_user.balance,
                transaction_type = TRANSFER
            )
            Transaction.objects.create(
                account = to_user,
                amount = amount,
                balance_after_transaction = current_user.balance,
                transaction_type = RECEIVED
            )
        return redirect('transfer')