from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home(request):
    return render(request, 'sample/home.html')


def logged_out(request):
    return render(request, 'sample/logged_out.html')
