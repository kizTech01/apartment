from django import forms
from .models import Apartment, ApartmentImage

class ApartmentForm(forms.ModelForm):
    amenities = forms.MultipleChoiceField(choices=[(x, x) for x in Apartment.AMENITIES], required=False, widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = Apartment
        fields = ("title", "description", "price", "location", "bedrooms", "bathrooms", "amenities")
        widgets = {"title": forms.TextInput(attrs={"class": "form-control"}), "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}), "price": forms.NumberInput(attrs={"class": "form-control", "min": 1}), "location": forms.Select(attrs={"class": "form-select"}), "bedrooms": forms.NumberInput(attrs={"class": "form-control", "min": 0}), "bathrooms": forms.NumberInput(attrs={"class": "form-control", "min": 0})}

class ImageForm(forms.ModelForm):
    class Meta:
        model = ApartmentImage
        fields = ("image", "is_primary")
        widgets = {"image": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/jpeg,image/png,image/webp"}), "is_primary": forms.CheckboxInput(attrs={"class": "form-check-input"})}
    def clean_image(self):
        image = self.cleaned_data["image"]
        if image.size > 5 * 1024 * 1024: raise forms.ValidationError("Image must be no larger than 5 MB.")
        return image

class SearchForm(forms.Form):
    location = forms.ChoiceField(required=False, choices=[("", "All locations")] + list(Apartment.Location.choices), widget=forms.Select(attrs={"class": "form-select"}))
    min_price = forms.DecimalField(required=False, min_value=0, widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Any minimum"}))
    max_price = forms.DecimalField(required=False, min_value=0, widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Any maximum"}))
    bedrooms = forms.IntegerField(required=False, min_value=0, widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Any", "min": 0}))
    amenities = forms.MultipleChoiceField(required=False, choices=[(x, x) for x in Apartment.AMENITIES], widget=forms.CheckboxSelectMultiple)
    sort = forms.ChoiceField(required=False, choices=[("newest", "Newest listings"), ("price", "Lowest price"), ("-price", "Highest price")], widget=forms.Select(attrs={"class": "form-select"}))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("min_price") is not None and cleaned_data.get("max_price") is not None and cleaned_data["min_price"] > cleaned_data["max_price"]:
            self.add_error("max_price", "Maximum price must be at least the minimum price.")
        return cleaned_data
