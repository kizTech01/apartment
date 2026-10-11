from django import forms

from accounts.models import User
from apartments.models import Apartment


class VerificationDecisionForm(forms.Form):
    decision = forms.ChoiceField(
        choices=[("APPROVED", "Approve verification"), ("REJECTED", "Reject verification")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Explain what the owner needs to correct."}),
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("decision") == "REJECTED" and not cleaned.get("rejection_reason", "").strip():
            self.add_error("rejection_reason", "Give the applicant a reason for the rejection.")
        return cleaned


class ListingDecisionForm(forms.Form):
    decision = forms.ChoiceField(
        choices=[(Apartment.Status.AVAILABLE, "Approve and publish"), (Apartment.Status.UNPUBLISHED, "Unpublish listing")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    moderation_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Optional note shown to the property owner."}),
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("decision") == Apartment.Status.UNPUBLISHED and not cleaned.get("moderation_note", "").strip():
            self.add_error("moderation_note", "Explain why this listing is being unpublished.")
        return cleaned


class ReportDecisionForm(forms.Form):
    decision = forms.ChoiceField(
        choices=[("RESOLVED", "Resolve report"), ("DISMISSED", "Dismiss report")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class UserAdministrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("full_name", "phone", "role", "is_verified", "is_active")
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "is_verified": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
