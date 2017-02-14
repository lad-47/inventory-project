from django.shortcuts import render

def manager_home(request):
	return render(request, 'manager_home.html');
