from django.contrib import admin


# Register ModelAdmin here.
class EmailModelAdmin(admin.ModelAdmin):
    list_display  = ['full_name']
    list_filter   = ['created_at', 'updated_at']
    search_fields = ['full_name', 'email']
    list_per_page = 10
    
    fieldsets = (
        ("Subscriber", {
            "classes" : ["extrapretty"],
            "fields" : ["full_name"],
        }),
        ("Personal information", {
            "classes" : ["collapse", "extrapretty"],
            "fields" : ["email"],
        }),
        ("Message", {
            "classes" : ["collapse", "extrapretty"],
            "fields" : ["content"],
        }),
    )