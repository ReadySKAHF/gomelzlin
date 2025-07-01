from django import template

register = template.Library()

@register.filter
def russian_pluralize(number, forms):
    """
    Правильное склонение для русского языка
    Использование: {{ count|russian_pluralize:"товар,товара,товаров" }}
    
    forms должно содержать 3 формы через запятую:
    - форма для 1 (товар)
    - форма для 2-4 (товара) 
    - форма для 5+ (товаров)
    """
    if not forms:
        return ''
    
    try:
        forms_list = [form.strip() for form in forms.split(',')]
        if len(forms_list) != 3:
            return forms
        
        # Преобразуем в число
        num = int(number)
        
        # Особые случаи для 11-14 (всегда множественное число)
        if 10 <= num % 100 <= 14:
            return forms_list[2]  # товаров
        
        # Обычные правила
        last_digit = num % 10
        
        if last_digit == 1:
            return forms_list[0]  # товар
        elif 2 <= last_digit <= 4:
            return forms_list[1]  # товара
        else:
            return forms_list[2]  # товаров
            
    except (ValueError, IndexError):
        return forms

@register.simple_tag
def products_count_text(count):
    """
    Специальная функция для отображения количества товаров
    Возвращает правильно склоненную строку: "5 товаров", "1 товар", "3 товара"
    """
    forms = "товар,товара,товаров"
    word = russian_pluralize(count, forms)
    return f"{count} {word}"

@register.filter  
def count_with_word(number, word_forms):
    """
    Альтернативный фильтр для склонения с числом
    Использование: {{ count|count_with_word:"товар,товара,товаров" }}
    """
    forms = word_forms.split(',')
    if len(forms) != 3:
        return f"{number} {word_forms}"
    
    try:
        num = int(number)
        
        # Особые случаи для 11-14
        if 10 <= num % 100 <= 14:
            word = forms[2].strip()
        else:
            last_digit = num % 10
            if last_digit == 1:
                word = forms[0].strip()
            elif 2 <= last_digit <= 4:
                word = forms[1].strip()
            else:
                word = forms[2].strip()
        
        return f"{num} {word}"
        
    except ValueError:
        return f"{number} {word_forms}"