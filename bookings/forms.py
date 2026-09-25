from django import forms
from django.utils import timezone
from .models import Booking
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking; fields = ("requested_date", "requested_time")
        widgets = {"requested_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}), "requested_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"})}
    def clean_requested_date(self):
        date = self.cleaned_data["requested_date"]
        if date < timezone.localdate(): raise forms.ValidationError("Please choose today or a future date.")
        return date
class BookingResponseForm(forms.ModelForm):
    class Meta:
        model = Booking; fields = ("status", "landlord_response")
        widgets = {"status": forms.Select(attrs={"class": "form-select"}), "landlord_response": forms.Textarea(attrs={"class": "form-control", "rows": 3})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.fields["status"].choices = [(x, y) for x, y in Booking.Status.choices if x in {"ACCEPTED", "DECLINED", "RESCHEDULED", "COMPLETED"}]
