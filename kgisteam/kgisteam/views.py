from django.shortcuts import render


def error_404(request, exception):
    return render(request, 'kgisteam/error_404.html', status=404)
