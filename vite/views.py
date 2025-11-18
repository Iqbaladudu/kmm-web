from django.shortcuts import render


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)


def test_404_view(request):
    """View untuk testing halaman 404 di development mode"""
    return render(request, '404.html', status=404)
