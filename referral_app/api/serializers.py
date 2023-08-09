from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.utils import model_meta

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Класс для сериализации модели пользователя - при запросах
    на чтение данных."""

    class Meta:
        model = User
        fields = (
            'id',
            'phone',
            'first_name',
            'last_name',
            'email',
            'invite_code',
            'granted_code',
        )
        read_only_fields = ('invite_code', 'phone',)

    def validate(self, data):
        granted_code = data.get('granted_code')

        if granted_code is None:
            return data
        request = self.context.get('request')
        user_id = request.parser_context.get('kwargs').get('pk')
        user = User.objects.get(id=user_id)
        if user.granted_code:
            raise serializers.ValidationError(
                'Повторный ввод кода недопустим'
            )
        if user.invite_code == granted_code:
            raise serializers.ValidationError(
                'Нельзя вводить собственный инвайт-код'
            )
        invite_codes = User.objects.filter(invite_code=granted_code)
        if not invite_codes:
            raise serializers.ValidationError(
                'Введенный инвайт-код не существует'
            )
        return data


class UserBriefSerializer(serializers.ModelSerializer):
    """Класс для сериализации модели пользователя - при запросах
    на чтение данных."""

    class Meta:
        model = User
        fields = (
            'phone',
        )
        read_only_fields = ('phone',)


class UserRetrieveSerializer(serializers.ModelSerializer):
    code_applicants = serializers.SerializerMethodField()

    def get_code_applicants(self, obj):
        queryset = (User.objects.values('phone')
                    .filter(granted_code=obj.invite_code)
                    .order_by('phone'))
        return UserBriefSerializer(queryset, read_only=True, many=True).data

    class Meta:
        model = User
        fields = (
            'id',
            'phone',
            'first_name',
            'last_name',
            'email',
            'invite_code',
            'granted_code',
            'code_applicants',
        )
        read_only_fields = ('phone',)


class UserCreateSerializer(serializers.Serializer):
    """Класс для сериализации модели пользователя - при запросах
    на создание пользователя."""
    id = serializers.IntegerField(
        label='Телефон',
        read_only=True
    )
    phone = serializers.IntegerField(
        label='Телефон',
        min_value=71000000000,
        max_value=79999999999,
    )
    default_error_messages = {
        'cannot_create_user': 'Не удалось создать пользователя'}

    def create(self, validated_data):
        try:
            with transaction.atomic():
                user = User.objects.create_user(**validated_data)

        except IntegrityError:
            users = User.objects.filter(phone=validated_data.get('phone'))
            if not users:
                self.fail('cannot_create_user')
            user = users.first()
            return self.update(user, validated_data)

        return user

    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance


class CustomAuthTokenSerializer(serializers.Serializer):
    """Класс для сериализации модели токена."""

    phone = serializers.IntegerField(
        label='Телефон',
        write_only=True
    )
    verification_code = serializers.CharField(
        label='Код верификации',
        write_only=True
    )
    token = serializers.CharField(
        label=_('Token'),
        read_only=True
    )

    def validate(self, attrs):
        phone = attrs.get('phone')
        verification_code = attrs.get('verification_code')

        if phone and verification_code:
            user = authenticate(
                request=self.context.get('request'),
                phone=phone,
                verification_code=verification_code,
            )
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
