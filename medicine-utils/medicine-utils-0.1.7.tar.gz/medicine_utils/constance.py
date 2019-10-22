
CONSTANCE_ADDITIONAL_FIELDS = {
    'char': ['django.forms.fields.CharField', {
        'widget': 'django.forms.TextInput',
        'widget_kwargs': dict(attrs={'size': 60}),
        'required': False
    }],
    'url': ['django.forms.fields.URLField', {
        'widget': 'django.forms.TextInput',
        'widget_kwargs': dict(attrs={'size': 60}),
        'required': False
    }],
}

CONSTANCE_ADDITIONAL_FIELDS.update(**{
    f'char_length_{n}': ['django.forms.fields.CharField', {
        'min_length': n,
        'max_length': n,
        'required': False,
        'widget': 'django.forms.TextInput',
        'widget_kwargs': dict(attrs={'size': 20})
    }] for n in range(1, 10)
})

CONSTANCE_ADDITIONAL_FIELDS.update(**{
    f'char_length_{n}_required': ['django.forms.fields.CharField', {
        'min_length': n,
        'max_length': n,
        'required': True,
        'widget': 'django.forms.TextInput',
        'widget_kwargs': dict(attrs={'size': 20})
    }] for n in range(1, 10)
})
