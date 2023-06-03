from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.auth.validators import ASCIIUsernameValidator


class User(AbstractUser):
    """Переопределенная модель пользователя"""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        'E-mail',
        max_length=settings.MAX_LENGTH_EMAIL,
        unique=True,
        help_text="Введите адрес электронной почты",
        validators=[ASCIIUsernameValidator()]
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=settings.MAX_LENGTH_USERNAME,
        unique=True,
        validators=[ASCIIUsernameValidator()]
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.MAX_LENGTH_FIRST_NAME
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.MAX_LENGTH_LAST_NAME
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик')
    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='following',
                                  verbose_name='Подписки')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'following'],
                                               name='unique_following')]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'