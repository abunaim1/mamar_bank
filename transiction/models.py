from django.db import models
from accounts.models import UserBankAccount
# Create your models here.
from .constants import TRANSACTION_TYPE

class Transaction(models.Model): 
    account = models.ForeignKey(UserBankAccount, related_name = 'transactions', on_delete = models.CASCADE) #ekjon user er multiple transactions hote pare jemon, se loan nibe abr withdraw korbe abr deposite korbe bla bla. 
    amount = models.DecimalField(decimal_places=2, max_digits = 12) #how much ammount he will transiction.
    balance_after_transaction = models.DecimalField(decimal_places=2, max_digits = 12)#transiction complete howar pore account e koto taka balance thaklo
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE, null = True) #kon dhoroner transiction korbe user, eta ki withdraw naki eta deposite kon type er transiction eta. 
    timestamp = models.DateTimeField(auto_now_add=True) #transiction er somoy ta.
    loan_approve = models.BooleanField(default=False) #loan nile oita back end theke approve korar jonne eita use kortesi 
    
    
    class Meta:
        ordering = ['timestamp'] #ei class ta ekhane use kora hoiche uporer transiction class er sathe extra charecteristics add korar jonne. jemon ekhane timestamp er vittite sokol transiction ke sort korlam. ordering ta sort korar jonne use hoi built in vabei. 

class BankCrupt(models.Model):
    is_bankcrupt = models.BooleanField(default=False, null=True, blank=True)
    