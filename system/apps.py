from django.apps import AppConfig



class SystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'system'

    def ready(self):
        ...
        #for data in UserContainer.objects.all():
        #    data.delete()
