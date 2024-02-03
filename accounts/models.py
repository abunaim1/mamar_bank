from django.db import models
from django.contrib.auth.models import User
from accounts.constants import ACCOUNT_TYPE, GENDER_TYPE
# ok. Why we create model? Model creates for connecting with database.


class UserBankAccount(models.Model): #models theke amra Model ke inherite koralm ekhane jate amra Model er moddhe ja kichu ogula ekhane use korte pari.

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')#django amader ekta built in User model diye rakhse oitake dhore ene ekhane one to one field er maddhme add kore dibo. karon ekjon user er sob information ekta korei thakbe. ekjon user er double name or any data double hoite pare na. so user model er sathe etar one to one relation ei hobe. ebong user model ke niye ashar sathe sathe amr nijer model er o kichu field thakbe ekhane.

    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE)
    account_no = models.IntegerField(unique=True) 
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_TYPE)
    initial_deposite_date = models.DateField(auto_now_add=True)
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2) # here default means first time blanace er value 0 set kora holo, then max_digits means sorboccho 12 digit er tk rakhte parbo, then decimal_place 2 mane dhoshomik er por 2 ta sonkha hobe. jemon = 100.12
    
    def __str__(self) -> str:
        return f'{self.account_no}'

class UserAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='address')
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.IntegerField()
    country = models.CharField(max_length=100)

    def __str__(self) -> str:
        return str(self.user.email)


