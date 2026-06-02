from django.db import models

class Company(models.Model):
    symbol = models.CharField(max_length=20, primary_key=True)
    company_name = models.CharField(max_length=200)
    sector = models.CharField(max_length=50)
    health_score = models.FloatField(default=0)
    roe = models.FloatField(default=0)
    opm = models.FloatField(default=0)
    debt_to_equity = models.FloatField(default=0)
    revenue_growth = models.FloatField(default=0)

    def __str__(self):
        return self.company_name


class FinancialData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    year = models.IntegerField()
    sales = models.BigIntegerField(default=0)
    net_profit = models.BigIntegerField(default=0)
    opm_pct = models.FloatField(default=0)
    eps = models.FloatField(default=0)

    class Meta:
        unique_together = ('company', 'year')
