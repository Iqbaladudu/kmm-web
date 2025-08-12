from django import forms
from django.contrib.auth import get_user_model
from .models import Student

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("User does not exist")

        user = User.objects.get(username=username)
        if not user.check_password(password):
            raise forms.ValidationError("Incorrect password")

        return cleaned_data

class StaffLoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not User.objects.filter(username=username, is_staff=True).exists():
            raise forms.ValidationError("Staff does not exist")

        user = User.objects.get(username=username)
        if not user.check_password(password):
            raise forms.ValidationError("Incorrect password")

        return cleaned_data

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['user']
        widgets = {
            # Text inputs dengan styling konsisten
            'full_name': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'birth_place': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'gender': forms.Select(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'marital_status': forms.Select(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'citizenship_status': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'region_origin': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'parents_name': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'parents_phone': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),

            # Academic fields
            'institution': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'faculty': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'major': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'degree_level': forms.Select(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'semester_level': forms.NumberInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'latest_grade': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),

            # Health Information
            'disease_history': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'disease_status': forms.Select(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),

            # Interests and Talents
            'sport_interest': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'sport_achievement': forms.Textarea(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary', 'rows': 3}),
            'art_interest': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'art_achievement': forms.Textarea(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary', 'rows': 3}),
            'literacy_interest': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'literacy_achievement': forms.Textarea(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary', 'rows': 3}),
            'science_interest': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'science_achievement': forms.Textarea(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary', 'rows': 3}),
            'mtq_interest': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'mtq_achievement': forms.Textarea(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary', 'rows': 3}),
            'media_interest': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'media_achievement': forms.Textarea(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary', 'rows': 3}),

            # Organizational History
            'organization_history': forms.Textarea(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary', 'rows': 4}),

            # Financial fields
            'education_funding': forms.Select(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'scholarship_source': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'living_cost': forms.NumberInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'monthly_income': forms.NumberInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),

            # Identity fields
            'passport_number': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'nik': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'lapdik_number': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'arrival_date': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'school_origin': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'umdah_name': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'umdah_phone': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'home_name': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'home_location': forms.TextInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
            'level': forms.Select(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),

            # File upload
            'photo': forms.ClearableFileInput(attrs={'class': 'mt-1 w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        return cleaned_data
