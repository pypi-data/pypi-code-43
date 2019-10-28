from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):

	def handle(self, *args, **options):
		if not User.objects.filter(username="admin").exists():
			print("Start create admin user...")
			print("...")
			User.objects.create_superuser("admin", "admin@mail.com", "Gfhjkm123")
			print("..")
			print(".")
			print("done!") 
		else:
			print("Admin was created, try to login")
