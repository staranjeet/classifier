from django.db import models

# Create your models here.
class News(models.Model):

	def __str__(self):
		return self.headline

	url =  models.CharField(max_length=200)
	headline = models.CharField(max_length=1000)
	content = models.CharField(max_length=1500)
	#note = models.CharField(max_length=1000)
	pub_date=models.DateTimeField('note date generated')
