from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Category, Product


class ProductSearchForm(forms.Form):
    """Форма поиска товаров"""
    
    q = forms.CharField(
        label=_('Поисковый запрос'),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите название товара, артикул или описание...',
            'autocomplete': 'off'
        })
    )
    
    category = forms.ModelChoiceField(
        label=_('Категория'),
        queryset=Category.objects.filter(parent__isnull=True, is_active=True),
        required=False,
        empty_label=_('Все категории'),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    subcategory = forms.ModelChoiceField(
        label=_('Подкатегория'),
        queryset=Category.objects.none(),  
        required=False,
        empty_label=_('Все подкатегории'),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    price_from = forms.DecimalField(
        label=_('Цена от'),
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0',
            'min': '0',
            'step': '0.01'
        })
    )
    
    price_to = forms.DecimalField(
        label=_('Цена до'),
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '999999',
            'min': '0',
            'step': '0.01'
        })
    )
    
    in_stock = forms.BooleanField(
        label=_('Только товары в наличии'),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    featured = forms.BooleanField(
        label=_('Только рекомендуемые'),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    sort = forms.ChoiceField(
        label=_('Сортировка'),
        choices=[
            ('name', _('По названию')),
            ('-name', _('По названию (убыв.)')),
            ('price', _('По цене (возр.)')),
            ('-price', _('По цене (убыв.)')),
            ('-created_at', _('Сначала новые')),
            ('created_at', _('Сначала старые')),
        ],
        required=False,
        initial='name',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.data.get('category'):
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Category.objects.filter(
                    parent_id=category_id,
                    is_active=True
                ).order_by('name')
            except (ValueError, TypeError):
                pass


class QuickSearchForm(forms.Form):
    """Быстрая форма поиска для шапки сайта"""
    
    q = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск товаров...',
            'autocomplete': 'off'
        })
    )


class ProductFilterForm(forms.Form):
    """Форма фильтрации товаров на странице категории"""
    
    price_from = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'От'
        })
    )
    
    price_to = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'До'
        })
    )
    
    in_stock = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    sort = forms.ChoiceField(
        choices=[
            ('name', 'По названию'),
            ('price', 'По цене ↑'),
            ('-price', 'По цене ↓'),
            ('-created_at', 'Новинки'),
        ],
        required=False,
        initial='name',
        widget=forms.Select(attrs={
            'class': 'form-control form-control-sm'
        })
    )