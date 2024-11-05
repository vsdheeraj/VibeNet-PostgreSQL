from django.contrib.auth import get_user_model    # that returns the user model currently active in this project.
from django.contrib.auth.forms import UserCreationForm

class UserCreateForm(UserCreationForm):
    class Meta:
        fields = ('username', 'email', 'password1', 'password2')
        model = get_user_model()          # to get current model who ever is accessing the website
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Display Name'     # setting up the label
        self.fields['email'].label = 'Email Address'
    