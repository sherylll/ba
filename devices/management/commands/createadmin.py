# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "homehubpi.settings")
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, UserManager
from ...models import Person

class Command(BaseCommand):
    help = 'create admin programatically'
    def add_arguments(self, parser):
        parser.add_argument('user_info', nargs='+', type=str)

    def handle(self, *args, **options):
        if len(User.objects.all()) != 0:
            #superuser is called pi by default
            User.objects.get(username="pi", is_superuser=True).delete()
            User.objects.all().delete()
            Person.objects.all().delete()
        #python manage.py createadmin name, email, password        
        user = User.objects.create_superuser(options['user_info'][0], options['user_info'][1], options['user_info'][2])
        
        user.save()
        
        superperson = Person()
        superperson.user = user
        
        #read key set
        f = open('keys.txt', 'r+')
        line =  f.readline().strip()
        superperson.keys = line
        superperson.uid = options['user_info'][3]
        f.write('')
        f.close()
        superperson.save()
        self.stdout.write(self.style.SUCCESS('Successfully created admin "%s" ' % options['user_info'][0] ))
