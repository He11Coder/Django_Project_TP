from django import forms
from .models import Profile, User, Question, Tag, Answer

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput)
    

class RegistrationForm(forms.Form):
    username = forms.CharField(required=True, min_length=3)
    email = forms.EmailField(required=False, widget=forms.EmailInput)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    password = forms.CharField(required=True, widget=forms.PasswordInput)
    password_check = forms.CharField(required=True, widget=forms.PasswordInput)
    avatar = forms.ImageField(required=False, widget=forms.FileInput)
    

    def clean_username(self):
        nick = self.cleaned_data['username']

        if User.objects.filter(username = nick).exists():
            self.add_error(field = 'username', error = 'Nickname already exists')

        return nick
    

    def clean_email(self):
        e_adress = self.cleaned_data['email']

        if (e_adress and User.objects.filter(email = e_adress).exists()):
            self.add_error(field = 'email', error = 'Email is already registered')

        return e_adress
    

    def clean_first_name(self):
        first = self.cleaned_data['first_name']

        if (first and len(first) < 3):
            self.add_error(field = 'first_name', error = 'Your first name must be longer than 3 letters')

        return first
    

    def clean_last_name(self):
        last = self.cleaned_data['last_name']

        if (last and len(last) < 3):
            self.add_error(field = 'last_name', error = 'Your last name must be longer than 3 letters')

        return last


    def clean(self):
        cleaned_data = super().clean()
        password_input = self.cleaned_data['password']
        password_conf = self.cleaned_data['password_check']

        if (password_input != password_conf):
            self.add_error(field = 'password', error = 'Password mismatch')
            self.add_error(field = 'password_check', error = 'Password mismatch')

        return cleaned_data
    

    def save(self):
        new_user = User.objects.create_user(username = self.cleaned_data['username'])
        new_user.set_password(self.cleaned_data['password'])

        profile = Profile.objects.create(user = new_user)
        new_user.save()

        e_adress = self.cleaned_data['email']
        first = self.cleaned_data['first_name']
        last = self.cleaned_data['last_name']
        ava = self.cleaned_data['avatar']

        if e_adress:
            new_user.email = e_adress

        if first:
            new_user.first_name = first
        
        if last:
            new_user.last_name = last

        if ava:
            profile.avatar.save(ava.name, ava)

        new_user.save()
        profile.save()

        
class ProfileEditForm(forms.Form):
    username = forms.CharField(required=False, min_length=3)
    email = forms.EmailField(required=True, widget=forms.EmailInput)
    old_password = forms.CharField(required = True, widget = forms.PasswordInput)
    new_password = forms.CharField(required = False, widget = forms.PasswordInput)
    new_password_check = forms.CharField(required = False, widget = forms.PasswordInput)
    avatar = forms.ImageField(required = False, widget = forms.FileInput)


    def clean_username(self):
        nick = self.cleaned_data['username']

        if (nick and User.objects.filter(username = nick).exists()):
            self.add_error(field = 'username', error = 'Nickname already exists')

        return nick
    

    def clean_email(self):
        e_adress = self.cleaned_data['email']

        if (e_adress and User.objects.filter(email = e_adress).exists()):
            self.add_error(field = 'email', error = 'Email is already registered')

        return e_adress
    

    def clean(self):
        cleaned_data = super().clean()
        new_pass = self.cleaned_data['new_password']
        new_pass_check = self.cleaned_data['new_password_check']

        if (new_pass and new_pass != new_pass_check):
            self.add_error(field = 'new_password', error = 'Password mismatch')
            self.add_error(field = 'new_password_check', error = 'Password mismatch')

        return cleaned_data
    

    def save(self, request):
        user = User.objects.get(username = request.user)
        profile = Profile.objects.get(user = user)

        nick = self.cleaned_data['username']
        e_adress = self.cleaned_data['email']
        new_pass = self.cleaned_data['new_password']
        ava = self.cleaned_data['avatar']

        if nick:
            user.username = nick
        
        if e_adress:
            user.email = e_adress

        if new_pass:
            user.set_password(new_pass)

        if ava:
            profile.avatar = ava

        user.save()
        profile.save()


class AskForm(forms.Form):
    title = forms.CharField(required=True, max_length=100)
    text = forms.CharField(required = True, widget = forms.Textarea)
    tags = forms.CharField(required = True, max_length = 50)

    def clean_tags(self):
        inputed_tags = self.cleaned_data['tags']

        all_tags = inputed_tags.split()
        for tag in all_tags:
            if len(tag) > 10:
                self.add_error(field = 'tags', error = 'Maximum length of one tag is 10 symbols (use a space to separate tags)')
                break

        return inputed_tags
    
    def save(self, request):
        user = User.objects.get(username = request.user)
        profile = Profile.objects.get(user = user)
        headline = self.cleaned_data['title']
        body = self.cleaned_data['text']
        all_tags = self.cleaned_data['tags'].split()

        new_question = Question.objects.create(title = headline, text = body, rating = 0, author_id = profile)

        for tag in all_tags:
            object_tag = Tag.objects.get_or_create(text = tag)
            new_question.tag.add(object_tag[0])

        new_question.save()

        return new_question.id

    
class AnswerForm(forms.Form):
    answer = forms.CharField(required = True, max_length = 1000, widget = forms.Textarea)

    def save(self, username, question_id):
        user = User.objects.get(username = username)
        profile = Profile.objects.get(user = user)
        question = Question.objects.get(id = question_id)
        answer_text = self.cleaned_data['answer']

        object_answer = Answer.objects.create(text = answer_text, rating = 0, question_id = question, author_id = profile)

        return object_answer