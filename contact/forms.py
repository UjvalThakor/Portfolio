from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    # Honeypot field for anti-spam (hidden from real users, bots fill it)
    website_check = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label="Do not fill"
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your Name or Company',
                'id': 'contact-name',
                'required': True,
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'your.email@domain.com',
                'id': 'contact-email',
                'required': True,
                'autocomplete': 'email',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Project inquiry / Opportunity / Architecture discussion',
                'id': 'contact-subject',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Tell me about the system, API, or opportunity you have in mind...',
                'id': 'contact-message',
                'rows': 5,
                'required': True,
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        honeypot = cleaned_data.get('website_check')
        if honeypot:
            raise forms.ValidationError("Spam detected. Bot rejection trigger.")
        return cleaned_data

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError("Please provide your real name (at least 2 characters).")
        return name

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 10:
            raise forms.ValidationError("Please write a meaningful message (at least 10 characters).")
        return message
