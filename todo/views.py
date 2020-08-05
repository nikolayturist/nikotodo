from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm, UserRegistrationForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator


def home(request):
    return render(request, 'todo/home.html')


# Create your views here.
def signupuser(request):
    if request.method == "GET":
        return render(request, 'todo/signup.html', {"user_creation_form": UserRegistrationForm()})
    else:
        try:
            registration_form = UserRegistrationForm(request.POST)
            if registration_form.is_valid():
                user = registration_form.save(False)
                user.is_active = False
                user.save(True)
                # --------------------------- #
                current_site = get_current_site(request)
                email_subject = 'Activate Your NikoTodo Account'
                message = render_to_string('todo/activate_account.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = registration_form.cleaned_data.get('email')
                email = EmailMessage(email_subject, message, to=[to_email])
                email.send()

                return redirect("account_activation")

                # --------------------------- #
                # login(request, user)
                # return redirect("currenttodos")
            else:
                return render(request, 'todo/signup.html', {"user_creation_form": registration_form,
                                                            "error": registration_form.errors})

        except ValidationError:
            return render(request, 'todo/signup.html', {"user_creation_form": UserRegistrationForm(),
                                                        "error": "Please enter valid email address"})
        except IntegrityError:
            return render(request, 'todo/signup.html', {"user_creation_form": UserRegistrationForm(),
                                                        "error": "The username has been already taken. "
                                                        "Please provide new username"})
        # try:
        #
        # if request.POST['password1'] == request.POST['password2']:
        #     try:
        #         user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
        #         user.email = request.POST['email']
        #         user.save()
        #         login(request, user)
        #         return redirect("currenttodos")
        #     except IntegrityError:
        #         return render(request, 'todo/signup.html', {"user_creation_form": UserRegistrationForm(),
        #                                                     "error": "The username has been already taken. "
        #                                                              "Please provide new username"})
        # else:
        #     return render(request, 'todo/signup.html', {"user_creation_form": UserRegistrationForm(),
        #                                                 "error": "Passwords didn't match"})


def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Your account has been activate successfully')
    else:
        return HttpResponse('Activation link is invalid!')


# Create your views here.
def loginuser(request):
    if request.method == "GET":
        return render(request, 'todo/login.html', {"user_login_form": AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user is None:
            return render(request, 'todo/login.html', {"user_login_form": AuthenticationForm(),
                                                       "error": "Username and password didn't match"})
        else:
            login(request, user)
            return redirect("currenttodos")


def account_activation(request):
    return render(request, 'todo/account_activation.html')

@login_required
def logoutuser(request):
    if request.method == "POST":
        logout(request)
        return redirect("home")


@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, completed_date__isnull=True)
    return render(request, 'todo/todos.html', {"todos": todos})


@login_required
def createtodo(request):
    if request.method == "GET":
        return render(request, 'todo/create.html', {"todo_form": TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect("currenttodos")

        except ValueError:
            return render(request, 'todo/create.html', {"todo_form": TodoForm(), "error": "Bad values passed in. Please try again"})


@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "GET":
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {"todo": todo, "todoform": form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect("currenttodos")
        except ValueError:
            return render(request, 'todo/viewtodo.html', {"todo": todo, "todoform": form, "error": "Bad values passed in. Please try again"})


@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        todo.completed_date = timezone.now()
        todo.save()
        return redirect("currenttodos")


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        todo.delete()
        return redirect("currenttodos")


@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, completed_date__isnull=False).order_by("-completed_date")
    return render(request, 'todo/completedtodos.html', {"todos": todos})
