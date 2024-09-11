from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,UserChangeForm,SetPasswordForm
from django import forms
from .models import *
from django.core.validators import RegexValidator



class ChangePasswordForm(SetPasswordForm):
    class Meta:
        model=Personne
        fields=('new_password1','new_password2')
    
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['new_password1'].label = ''
        self.fields['new_password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['new_password2'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['new_password2'].label = ''
        self.fields['new_password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'     
        
        
class UpdateUserForm(UserChangeForm):
    #hide password getting in form
    password=None
    email = forms.EmailField(
        label="",
        
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Adresse Email','readonly': 'readonly'}),
        validators=[RegexValidator(regex=r'[a-zA-Z0-9._%+-]+@(umi\.ac\.ma|edu\.umi\.ac\.ma)', message='Veuillez fournir une adresse email valide se terminant par umi.ac.ma ou edu.umi.ac.ma')]
    )
    nom = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Nom'}),required=False)
    prenom = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Prenom'}),required=False)
    telephone=forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Telephone'}),required=False)
    class Meta:
        model = Personne
        fields = ('email','nom', 'prenom', 'telephone')

    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)

       

    def clean_username(self):
        email = self.cleaned_data.get('email')
        if Personne.objects.filter(email=email).exists():
            raise forms.ValidationError('Cet Email existe déja!')
        return email
    
    
    
    
    
    
    
    
class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        label="",
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Adresse Email'}),
        validators=[RegexValidator(regex=r'[a-zA-Z0-9._%+-]+@(umi\.ac\.ma|edu\.umi\.ac\.ma)', message='Veuillez fournir une adresse email valide se terminant par umi.ac.ma ou edu.umi.ac.ma')]
    )
    prenom = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Prenom'}))
    nom = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Nom'}))
    telephone = forms.CharField(
        label="",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telephone'}),
        validators=[RegexValidator(
            regex=r'^(?:\+212[5-7]\d{8}|0[5-7]\d{8})$', 
            message='Veuillez fournir un numéro de téléphone valide au format marocain (+212XXXXXXXXX ou 0XXXXXXXXX)'
        )]
    )
    

    class Meta:
        model = Personne
        fields = ('nom', 'prenom', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        
        self.fields['nom'].help_text = '<br>'
        self.fields['prenom'].help_text = '<br>'
        self.fields['telephone'].help_text = '<br>'

        self.fields['email'].help_text = '<br>'
        
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Mot de passe'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Votre mot de passe ne peut pas être trop similaire à vos autres informations personnelles.</li><li>Votre mot de passe doit contenir au moins 8 caractères.</li><li>Votre mot de passe ne peut pas être un mot de passe couramment utilisé.</li><li>Votre mot de passe ne peut pas être entièrement numérique.</li></ul><br>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirmer votre mot de passe'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Entrez le même mot de passe qu\'auparavant, pour vérification</small><br></span><br>'


    def save(self, commit=True, image_data=None):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.nom = self.cleaned_data["nom"]
        user.prenom = self.cleaned_data["prenom"]
        user.telephone = self.cleaned_data["telephone"]
        if image_data:
            # If image data is provided, decode and save it
            format, imgstr = image_data.split(';base64,') 
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{user.email}.{ext}')
            user.image.save(f'{user.email}.{ext}', data, save=True)
        if commit:
            user.save()
        return user
    
    
    
    def clean_username(self):
        email = self.cleaned_data.get('email')
        if Personne.objects.filter(email=email).exists():
            raise forms.ValidationError('Cet Email existe déja!')
        return email


# class UserInfoForm(forms.ModelForm):
     
#     phone=forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Phone'}),required=False)
#     adresse1=forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Addresse 1'}),required=False)
#     adresse2=forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Addresse 2'}),required=False)
#     city=forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'City'}),required=False)
#     state=forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'State'}),required=False)
#     zipcode=forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Zip Code'}),required=False)
#     country=forms.CharField(label="",widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Country'}),required=False)
    
#     class Meta:
#         model = Profile
#         fields= ('phone','adresse1','adresse2','city','state','zipcode','country')