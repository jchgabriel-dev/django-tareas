from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def signup(request):
    
    if request.method == "GET":
        print("Enviando formulario")
    else:
        post = request.POST
        if post["password1"] != post["password2"]:
           return HttpResponse("Contraseñas no coinciden")
        else:
            try:
               
                user = User.objects.create_user(
                    username=post["username"], 
                    password=post["password2"])
                
                user.save()
                login(request, user)
                return redirect("tasks")
            
            except Exception as e:
                return HttpResponse(f"Error al crear usuario: {e}")
           

    
    return render(request, "signup.html",{
        'form': UserCreationForm
    })


def home(request):
    return render(request, "home.html")


@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, dateCompleted__isnull=True)

    return render(request, "tasks.html", {
        'tasks': tasks
    })

@login_required
def TaskListComplete(request):
    tasks = Task.objects.filter(user=request.user, dateCompleted__isnull=False)

    return render(request, "tasks.html", {
        'tasks': tasks
    })

@login_required
def signout(request):
    logout(request)
    return redirect("home")



def signin(request):
    if request.method == "GET":
        return render(request, "signin.html", {
            'form': AuthenticationForm
        })

    else:
        print(request.POST)
        post = request.POST
        user = authenticate(request, username=post["username"], password=post["password"])

        if user is None:
            return render(request, "signin.html", {
                'form': AuthenticationForm,
                'error': "No encontrado"
            })
        else:
            login(request, user)
            return redirect("tasks")

      

@login_required
def createTask(request):
    if request.method == "GET":
        return render(request, 'taskCreate.html', {
            'form': TaskForm
        })
    
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect("tasks")
        except:
            return HttpResponse("fallo")


@login_required
def TaskDetailView(request, task_id):
    if request.method == "GET":
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, "TaskDetailTemplate.html", {
            'task': task,
            'form': form
        })
    
    else:
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(request.POST, instance=task)
        form.save()

        return redirect("tasks")

    
@login_required  
def TaskCompleteView(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.dateCompleted = timezone.now()
        task.save()
        return redirect("tasks")

@login_required
def TaskDeleteView(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        task.delete()
        return redirect("tasks")