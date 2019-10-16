from django.core.exceptions import ValidationError
from django.db import models

from integration_utils.fields import UTF8JSONField

class BaseAPIMethod(models.Model):
	name = models.CharField(max_length=255, db_index=True)
	endpoint = models.CharField(max_length=500, blank=True, null=True)
	request_method 	 = models.CharField(max_length=15, default="get", choices=(
			("get", "get"),
			("post", "post"),
		))
	is_filter_method = models.BooleanField(default=False)
	is_data_method = models.BooleanField(default=False)
	params  = UTF8JSONField(default={}, blank=True, null=True)
	definition  = UTF8JSONField(default={
		"change_keys": {},
		"default": {},
		"append_enums": False,
		})

	class Meta:
		pass

	def __str__(self):
		return f"{self.name} - {self.endpoint}"


class CustomAPIMethod(models.Model):
	name = models.CharField(max_length=255, db_index=True)
	config 	= UTF8JSONField(
		default={
			"methods": {}	
		}
	)
	definition = UTF8JSONField(default={
		})
	
	class Meta:
		pass

	def __str__(self):
		return self.name
