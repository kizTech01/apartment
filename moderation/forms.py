from django import forms
from .models import ListingReport
class ListingReportForm(forms.ModelForm):
    class Meta:
        model = ListingReport; fields = ("reason", "description")
        widgets = {"reason": forms.Select(attrs={"class": "form-select"}), "description": forms.Textarea(attrs={"class": "form-control", "rows": 3})}
