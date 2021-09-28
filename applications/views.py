from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from .models import AjaxSliderModel

def index(request):
	return render(request, 'applications/index.html', {})

def ajax_number(request):
	num = request.POST.get('num')
	print(num)
	AjaxSliderModel.objects.update_or_create(
		md_name='AjaxSliderNum',
		defaults={'md_num':num}
	)
	d = {'num': num,
			 # 'minus': minus,
			 }
	return JsonResponse(d)