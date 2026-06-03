from django.db import models

class Company(models.Model):
    symbol = models.CharField(max_length=20, primary_key=True)
    company_name = models.CharField(max_length=200)
    sector = models.CharField(max_length=50, default="Other")
    health_score = models.FloatField(default=70)
    roe = models.FloatField(default=15)
    opm = models.FloatField(default=18)
    debt_to_equity = models.FloatField(default=0.3)
    revenue_growth = models.FloatField(default=10)

    def __str__(self):
        return f"{self.symbol} - {self.company_name}"

    @property
    def health_label(self):
        if self.health_score >= 85:
            return 'EXCELLENT'
        elif self.health_score >= 70:
            return 'GOOD'
        elif self.health_score >= 50:
            return 'AVERAGE'
        elif self.health_score >= 35:
            return 'WEAK'
        else:
            return 'POOR'


class FinancialData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='financials')
    year = models.IntegerField()

    # Profit & Loss
    sales = models.BigIntegerField(default=0)
    net_profit = models.BigIntegerField(default=0)
    opm_pct = models.FloatField(default=0)
    eps = models.FloatField(default=0)

    # Balance Sheet
    total_assets = models.BigIntegerField(default=0)
    borrowings = models.BigIntegerField(default=0)
    reserves = models.BigIntegerField(default=0)
    debt_to_equity_calc = models.FloatField(default=0)

    class Meta:
        unique_together = ('company', 'year')
        ordering = ['-year']

    def __str__(self):
        return f"{self.company.symbol} - {self.year}"
