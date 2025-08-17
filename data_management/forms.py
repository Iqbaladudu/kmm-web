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

class StaffStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'full_name','email','whatsapp_number','birth_place','birth_date','gender',
            'marital_status','citizenship_status','region_origin','parents_name',
            'institution','faculty','major','degree_level','semester_level','latest_grade',
            'passport_number','nik','lapdik_number','arrival_date','school_origin',
            'home_name','home_location','level',
            'disease_history','disease_status',
            'sport_interest','sport_achievement','art_interest','art_achievement',
            'literacy_interest','literacy_achievement','science_interest','science_achievement',
            'mtq_interest','mtq_achievement','media_interest','media_achievement',
            'organization_history','is_draft'
        ]
        widgets = {
            # Text inputs dengan styling konsisten
            'full_name': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'birth_place': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'citizenship_status': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'region_origin': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'parents_name': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'institution': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'faculty': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'major': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'latest_grade': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'passport_number': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'nik': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'lapdik_number': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'school_origin': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'home_name': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'home_location': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'sport_interest': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'art_interest': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'literacy_interest': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'science_interest': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'mtq_interest': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'media_interest': forms.TextInput(attrs={'class': 'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),

            # Hidden fields
            'is_draft': forms.HiddenInput(),

            # Date fields
            'birth_date': forms.DateInput(attrs={'type':'date','class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'arrival_date': forms.DateInput(attrs={'type':'date','class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),

            # Number fields
            'semester_level': forms.NumberInput(attrs={'class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),

            # Select fields
            'gender': forms.Select(attrs={'class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'marital_status': forms.Select(attrs={'class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'degree_level': forms.Select(attrs={'class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'level': forms.Select(attrs={'class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'disease_status': forms.Select(attrs={'class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),

            # Textarea fields
            'sport_achievement': forms.Textarea(attrs={'rows':2,'class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'art_achievement': forms.Textarea(attrs={'rows':2,'class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'literacy_achievement': forms.Textarea(attrs={'rows':2,'class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'science_achievement': forms.Textarea(attrs={'rows':2,'class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'mtq_achievement': forms.Textarea(attrs={'rows':2,'class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
            'media_achievement': forms.Textarea(attrs={'rows':2,'class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),

            # Organizational History
            'organization_history': forms.Textarea(attrs={'rows':3,'class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),

            # Disease History
            'disease_history': forms.TextInput(attrs={'class':'mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-500 text-sm'}),
        }
