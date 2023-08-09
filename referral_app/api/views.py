import datetime as dt

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import mixins, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from users.tasks import send_sms
from users.utils import generate_sequense

from .permissions import IsOwnerOrReadOnly
from .serializers import (CustomAuthTokenSerializer, UserCreateSerializer,
                          UserRetrieveSerializer, UserSerializer)

User = get_user_model()


class UserViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                  mixins.ListModelMixin, GenericViewSet):
    """Класс для обработки эндпойнтов на вывод списка пользователей
    и эндпойнтов конкретного пользователя (просмотр и изменение
    данных)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('retrieve',):
            return UserRetrieveSerializer
        return UserSerializer


class UserCreateView(APIView):
    """Класс для обработки эндпойнта на создание пользователя."""

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            code = generate_sequense(4, digits_only=True)
            deadline = dt.datetime.utcnow().timestamp() + settings.VERIF_TIME
            serializer.save(verification_code=code,
                            verif_cutoff_timestamp=deadline)
            send_sms.delay(
                phone=serializer.validated_data.get('phone'),
                code=code,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class CustomObtainAuthToken(ObtainAuthToken):
    """Класс для обработки эндпойнта верификации пользователя.
    После верификации создается возвращается токен авторизации."""

    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user.create_invite_code()
        return Response({'token': token.key})
