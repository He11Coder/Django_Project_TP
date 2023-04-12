from askme.models import Profile, Tag


def top_users(request):
    result = Profile.objects.all()[:10]
    return {
        'top_users' : result
    }


def top_tags(request):
    result = Tag.objects.all()[:10]
    return {
        'top_tags' : result
    }
