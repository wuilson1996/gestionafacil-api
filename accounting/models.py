from django.db import models
from user.models import Employee
from company.models import Branch
from customer.models import Customer
from invoice.models import Invoice

class Transaction(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50)  # Tipo de transacción (venta, reembolso, etc.)
    amount = models.FloatField()  # Monto de la transacción
    date = models.DateField(auto_now_add=True)  # Fecha de la transacción
    description = models.TextField(null=True, blank=True)  # Descripción de la transacción

class Account(models.Model):
    name = models.CharField(max_length=100)  # Nombre de la cuenta contable
    description = models.TextField(null=True, blank=True)  # Descripción de la cuenta contable

class JournalEntry(models.Model):
    date = models.DateField()  # Fecha del asiento contable
    description = models.TextField(null=True, blank=True)  # Descripción del asiento contable
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Empleado responsable del asiento contable
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)  # Sucursal asociada al asiento contable

class JournalEntryItem(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE)  # Asiento contable asociado
    account = models.ForeignKey(Account, on_delete=models.CASCADE)  # Cuenta contable asociada
    debit = models.FloatField(default=0)  # Monto debitado en la cuenta contable
    credit = models.FloatField(default=0)  # Monto acreditado en la cuenta contable