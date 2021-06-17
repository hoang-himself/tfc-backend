from django.conf import settings

from master_db.models import (
    Metatable, Branch, Setting, Role, Course,
    ClassMetadata, ClassStudent, ClassTeacher, Session, Attendance, Log
)
from master_db.serializers import (
    MetatableSerializer, BranchSerializer, SettingSerializer, RoleSerializer, UserSerializer, CourseSerializer,
    ClassMetadataSerializer, ClassStudentSerializer, ClassTeacherSerializer, SessionSerializer, AttendanceSerializer, LogSerializer
)

import datetime
import jwt


def generate_access_token(user):
    access_token_payload = {
        'user_id': user.get('username'),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=15),
        'iat': datetime.datetime.utcnow(),
    }

    access_token = jwt.encode(access_token_payload,
                              settings.JWT_ACCESS_KEY, algorithm='HS256').decode('utf-8')
    return access_token


def generate_refresh_token(user):
    refresh_token_payload = {
        'user_id': user.get('username'),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=14),
        'iat': datetime.datetime.utcnow()
    }
    refresh_token = jwt.encode(refresh_token_payload,
                               settings.JWT_REFRESH_KEY, algorithm='HS256').decode('utf-8')
    return refresh_token


def get_setting_session(request):
    if request.session.get('setting', -1) != -1:
        request.session.set('setting', SettingSerializer(
            Setting.objects.all(), many=True).data)
