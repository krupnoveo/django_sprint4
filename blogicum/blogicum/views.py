from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog:index')
    else:
        form = UserCreationForm()

    context = {'form': form}
    template = 'registration/registration_form.html'
    return render(request, template, context)
