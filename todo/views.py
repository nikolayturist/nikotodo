from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'todo/home.html')


# Create your views here.
def signupuser(request):
    if request.method == "GET":
        return render(request, 'todo/signup.html', {"user_creation_form": UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect("currenttodos")
            except IntegrityError:
                return render(request, 'todo/signup.html', {"user_creation_form": UserCreationForm(),
                                                            "error": "The username has been already taken. "
                                                                     "Please provide new username"})
        else:
            return render(request, 'todo/signup.html', {"user_creation_form": UserCreationForm(),
                                                        "error": "Passwords didn't match"})


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
