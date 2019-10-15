from django.shortcuts import render

def preview(request):
    return render(request, 'preview.html', {})
