from django.db import models

class SearchQueryModel(models.Model):
	objects				=models.Manager()
	md_query_name	=models.CharField(max_length=50,null=True)
	md_srch_url		=models.TextField(null=True)
	md_ex_title		=models.TextField(null=True)
	md_ex_seller	=models.TextField(null=True)
	md_alert_sw		=models.CharField(max_length=50,null=True)
	md_sokketu_sw	=models.CharField(max_length=50,null=True)
	md_autoex_sw	=models.CharField(max_length=50,null=True)
	md_newurl			=models.TextField(null=True)
	md_oldurl			=models.TextField(null=True)
	def __str__(self):
		return 'id:'+str(self.id)+' name:'+str(self.md_query_name)

class UserDataModel(models.Model):
	objects				=models.Manager()
	md_name				=models.CharField(max_length=50,null=True)
	md_line_token	=models.CharField(max_length=100,null=True)
	def __str__(self):
		return 'id:'+str(self.id)+' name:'+str(self.md_name)