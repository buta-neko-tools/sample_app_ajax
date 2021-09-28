from django.db import models

class AjaxSliderModel(models.Model):
	objects	=models.Manager()
	md_name	=models.CharField(max_length=50,null=True)
	md_num	=models.CharField(max_length=50,null=True)
	def __str__(self):
		return 'id:'+str(self.id) + 'num:'+str(self.md_num)