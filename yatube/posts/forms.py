from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group']
        labels = {
            'text': _('Пост'),
            'group': _('Имя группы'),
        }
        help_texts = {
            'text': _('Поле для ввода содержимого поста.'),
            'group': _('Выбрать группу, где будет запощен пост'),
        }
