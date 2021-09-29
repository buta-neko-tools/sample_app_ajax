from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from .models import AjaxSliderModel

def index(request):
	return render(request, 'applications/index.html', {})

def ajax_number(request):
	num = request.POST.get('num')
	print(num)
	AjaxSliderModel.objects.update_or_create(md_name='AjaxSliderNum',
																					 defaults={'md_num':num},
																					 )
	d = {'num': num,
			 }
	return JsonResponse(d)

def dballdata(request):
	try:
		dballdata=AjaxSliderModel.objects.get(md_name='AjaxSliderNum')
		db_num=dballdata.md_num
	except:
		db_num='0'
	dt_data={'db_num':db_num}
	return render(request, 'applications/dballdata.html',dt_data)
