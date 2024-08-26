from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import (CASCADE, CharField, EmailField, ForeignKey,
                              Model, UniqueConstraint)


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    email = EmailField(
        verbose_name='Почта',
        max_length=settings.MAX_LENGHT_USER_EMAIL,
        unique=True,
    )
    password = CharField(
        verbose_name='Пароль',
        max_length=settings.MAX_LENGHT_USER_PASSWORD,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(Model):
    user = ForeignKey(
        User,
        related_name='subscriber',
        verbose_name='Подписчик',
        help_text='Подписчик',
        on_delete=CASCADE,
    )
    author = ForeignKey(
        User,
        related_name='subscribing',
        verbose_name='Автор',
        help_text='Автор',
        on_delete=CASCADE,
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='Нельзя подписаться на самого себя',
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def clean(self):
        if self.author == self.user:
            raise ValidationError('Нельзя подписаться на самого себя')
        if Subscribe.objects.filter(
            user=self.user, author=self.author
        ).exists():
            raise ValidationError('Вы уже подписаны на этого автора')
        return super().save(self)

    def __str__(self):
        return f'{self.user.username} подписался на {self.author.username}'
