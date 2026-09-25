from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import LandlordVerification, Preference, User


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("full_name", "email", "phone", "password1", "password2")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): field.widget.attrs["class"] = "form-control"


class LandlordRegistrationForm(RegistrationForm):
    role = forms.ChoiceField(choices=[(User.Role.LANDLORD, "Landlord"), (User.Role.AGENT, "Agent")])
    business_name = forms.CharField(required=False, help_text="Optional business or property-management name.")
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]
        if commit: user.save()
        return user


class LoginForm(AuthenticationForm):
    account_type = forms.ChoiceField(
        choices=[("TENANT", "Tenant"), ("LANDLORD", "Landlord")],
        label="Sign in as",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    username = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    field_order = ["account_type", "username", "password"]

    def clean(self):
        cleaned_data = super().clean()
        user = self.get_user()
        account_type = cleaned_data.get("account_type")

        if user and account_type == "TENANT" and user.role != User.Role.TENANT:
            raise forms.ValidationError("This account is registered as a landlord. Please choose Landlord.")
        if user and account_type == "LANDLORD" and user.role not in {User.Role.LANDLORD, User.Role.AGENT}:
            raise forms.ValidationError("This account is registered as a tenant. Please choose Tenant.")
        return cleaned_data


class VerificationForm(forms.ModelForm):
    class Meta:
        model = LandlordVerification
        fields = ("document_type", "document")
        widgets = {"document_type": forms.Select(attrs={"class": "form-select"}), "document": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".pdf,image/*"})}
    def clean_document(self):
        file = self.cleaned_data["document"]
        if file.size > 5 * 1024 * 1024: raise forms.ValidationError("Document must be 5 MB or smaller.")
        return file


class PreferenceForm(forms.ModelForm):
    amenities_wanted = forms.MultipleChoiceField(required=False, choices=[], widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = Preference
        fields = ("min_price", "max_price", "preferred_location", "min_bedrooms", "amenities_wanted")
        widgets = {"min_price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 300000"}), "max_price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 600000"}), "preferred_location": forms.Select(attrs={"class": "form-select"}), "min_bedrooms": forms.NumberInput(attrs={"class": "form-control", "min": 0})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apartments.models import Apartment
        self.fields["preferred_location"].choices = [("", "Any Yola/Jimeta location")] + list(Apartment.Location.choices)
        self.fields["amenities_wanted"].choices = [(x, x) for x in Apartment.AMENITIES]
