from django.utils import timezone


def year(request):
    d = timezone.now()

    return {
        'year': d.year
    }
