from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from askme.models import Profile, Question, Answer, Tag


class Command(BaseCommand):
    help = u'Fills database with the only parameter [rate]'


    def add_arguments(self, parser):
        parser.add_argument('ratio', type = int, help = u'Specifies the number of generated data')


    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']

        tags = [Tag(text = get_random_string(5, "ABCDE12345")) for i in range(ratio)]
        Tag.objects.bulk_create(tags)

        users = [User.objects.create_user(username = get_random_string(8, "userx67890"), email = '', password = 'userofsegfault') for i in range(ratio)]
        User.objects.bulk_create(users)

        profiles = [Profile(user = users[i]) for i in range(ratio)]
        Profile.objects.bulk_create(profiles)
