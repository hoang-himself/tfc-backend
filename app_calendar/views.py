from django.views.decorators.csrf import csrf_protect

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app_auth.utils import has_perm
from master_db.models import Calendar

# Create your views here.


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def list_calendar(request):
    """
        Return list of users with a specified view
    """
    check = has_perm(request, ['account_cred'])
    if check.status_code >= 400:
        return check

    filter_query = request.GET.getlist('filter')

    print(filter_query)
    if not filter_query:
        filter_query = [
            'user__uuid',
            'name',
            'desc',
            'time_start',
            'time_end',
            'created_at',
            'updated_at',
        ]

    filter_dict = {
        'user__uuid': True,
        'name': True,
        'desc': True,
        'time_start': True,
        'time_end': True,
        'created_at': True,
        'updated_at': True,
    }

    listZ = []
    for key in filter_query:  # Query filter for choosing views
        if filter_dict[key]:
            listZ.append(key)

    # Asterisk expands list into separated args
    # https://docs.python.org/2/tutorial/controlflow.html#unpacking-argument-lists
    data = Calendar.objects.all().values(*listZ)
    return Response(data)
