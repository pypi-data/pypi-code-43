from django.contrib import admin
from .models import BaseAPIMethod, CustomAPIMethod

class BaseAPIMethodAdmin(admin.ModelAdmin):
	list_display 	= ("name", "endpoint",'request_method', "is_filter_method", "is_data_method")
	list_filter 	= ("is_filter_method", 'request_method', "is_data_method")
	list_editable 	= ("is_filter_method", 'request_method', "is_data_method")
	search_fields 	= ("name", "endpoint")

	class Meta:
		model = BaseAPIMethod

admin.site.register(BaseAPIMethod, BaseAPIMethodAdmin)
admin.site.register(CustomAPIMethod)
