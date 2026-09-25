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
    location = forms.ChoiceField(required=False, choices=[("", "All locations")] + list(Apartment.Location.choices))
    min_price = forms.DecimalField(required=False, min_value=0)
    max_price = forms.DecimalField(required=False, min_value=0)
    bedrooms = forms.IntegerField(required=False, min_value=0)
    amenities = forms.MultipleChoiceField(required=False, choices=[(x, x) for x in Apartment.AMENITIES])
    sort = forms.ChoiceField(required=False, choices=[("newest", "Newest listings"), ("price", "Lowest price"), ("-price", "Highest price")])
