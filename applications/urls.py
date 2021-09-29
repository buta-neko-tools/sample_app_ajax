from django.urls import path
from . import views

app_name='app_urls'

urlpatterns = [
	# path('v1/',views.input_v1,name='input'),
	# path('userdata/',views.userdata,name='userdata'),
	# path('dballdata/',views.dballdata,name='dballdata'),
	# path('test01/',views.test01,name='test01'),

	path('index/',views.index,name='index'),
	path('ajax-number/',views.ajax_number,name='ajax_number'),
	path('dballdata/',views.dballdata,name='dballdata'),
]