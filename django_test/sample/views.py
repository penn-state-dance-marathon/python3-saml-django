from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home(request):
    """Return home template."""
    return render(request, 'sample/home.html')


def logged_out(request):
    """Return logged out template."""
    return render(request, 'sample/logged_out.html')
