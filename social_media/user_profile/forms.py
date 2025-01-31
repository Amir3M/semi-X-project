from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from home.models import Post, Tag
        

class UserProfileForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'password1', 'password2', 'email']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        
        # Remove help texts for all fields
        for field_name, field in self.fields.items():
            field.help_text = ''

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'bio', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserProfile.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '4',
            'placeholder': 'What\'s on your mind?'
        })
    )
    
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = Post
        fields = ['content', 'image', 'tags']

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) == 0:
            raise forms.ValidationError("Content cannot be empty.")
        return content

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Save tags after the instance is saved
            self.save_m2m()  # This is needed for ManyToMany fields
        return instance