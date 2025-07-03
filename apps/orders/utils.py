from decimal import Decimal
from django.conf import settings
from .models import Order, OrderItem
from apps.accounts.models import UserProfile, CompanyProfile, DeliveryAddress


def get_user_order_defaults(user):
    """
    Получает данные пользователя для автозаполнения формы заказа
    """
    defaults = {
        'customer_name': user.get_full_name(),
        'customer_email': user.email,
        'customer_phone': user.phone or '',
        'company_name': '',
        'company_unp': '',
        'company_address': '',
        'delivery_address': '',
        'default_address_id': None,
    }
    
    # Получаем профиль пользователя
    try:
        profile = user.profile
        if profile.city and profile.address:
            defaults['delivery_address'] = profile.get_full_address()
    except UserProfile.DoesNotExist:
        pass
    
    # Если пользователь - юридическое лицо, получаем данные компании
    if user.is_company:
        try:
            company_profile = user.company_profile
            defaults.update({
                'company_name': company_profile.company_name or '',
                'company_unp': company_profile.unp or '',
                'company_address': company_profile.legal_address or '',
            })
        except CompanyProfile.DoesNotExist:
            pass
    
    # Получаем адрес доставки по умолчанию
    try:
        default_address = DeliveryAddress.objects.get(
            user=user,
            is_default=True,
            is_active=True
        )
        defaults['default_address_id'] = default_address.id
        defaults['delivery_address'] = default_address.get_full_address()
    except DeliveryAddress.DoesNotExist:
        pass
    
    return defaults


def calculate_delivery_cost(delivery_method, delivery_address=None, cart_total=None):
    """
    Рассчитывает стоимость доставки в зависимости от метода и суммы заказа
    """
    delivery_costs = {
        'pickup': Decimal('0.00'),
        'delivery': Decimal('10.00'),  # Доставка по городу
        'transport_company': Decimal('0.00'),  # По согласованию
    }
    
    base_cost = delivery_costs.get(delivery_method, Decimal('0.00'))
    
    # Бесплатная доставка для заказов свыше определенной суммы
    if cart_total and cart_total >= Decimal('500.00') and delivery_method == 'delivery':
        return Decimal('0.00')
    
    return base_cost


def validate_order_data(order_data):
    """
    Валидирует данные заказа перед созданием
    """
    errors = []
    
    # Проверяем обязательные поля
    required_fields = {
        'customer_name': 'Имя заказчика',
        'customer_email': 'Email заказчика',
        'customer_phone': 'Телефон заказчика',
    }
    
    for field, label in required_fields.items():
        if not order_data.get(field, '').strip():
            errors.append(f'Поле "{label}" обязательно для заполнения')
    
    # Проверяем email
    import re
    email = order_data.get('customer_email', '').strip()
    if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors.append('Некорректный email адрес')
    
    # Проверяем телефон
    phone = order_data.get('customer_phone', '').strip()
    if phone and not re.match(r'^\+?[\d\s\-\(\)]{7,}$', phone):
        errors.append('Некорректный номер телефона')
    
    # Проверяем УНП для юридических лиц
    unp = order_data.get('company_unp', '').strip()
    if unp and not re.match(r'^\d{9}$', unp):
        errors.append('УНП должен содержать 9 цифр')
    
    # Проверяем адрес доставки для доставки
    delivery_method = order_data.get('delivery_method', 'pickup')
    if delivery_method != 'pickup':
        delivery_address = order_data.get('delivery_address', '').strip()
        if not delivery_address:
            errors.append('Укажите адрес доставки')
    
    return errors


def format_order_for_notification(order):
    """
    Форматирует данные заказа для уведомлений
    """
    items_text = []
    for item in order.items.all():
        items_text.append(f"- {item.product.name} x{item.quantity} = {item.get_total_price()} BYN")
    
    delivery_info = f"Способ доставки: {order.get_delivery_method_display()}"
    if order.delivery_address:
        delivery_info += f"\nАдрес доставки: {order.delivery_address}"
    
    payment_info = f"Способ оплаты: {order.get_payment_method_display()}"
    
    formatted_text = f"""
Новый заказ #{order.number}

Заказчик: {order.customer_name}
Email: {order.customer_email}
Телефон: {order.customer_phone}

{"Организация: " + order.company_name if order.company_name else ""}
{"УНП: " + order.company_unp if order.company_unp else ""}

Товары:
{chr(10).join(items_text)}

{delivery_info}

{payment_info}

Общая сумма: {order.total_amount} BYN

{"Комментарий: " + order.notes if order.notes else ""}

Дата заказа: {order.created_at.strftime('%d.%m.%Y %H:%M')}
    """.strip()
    
    return formatted_text


def get_order_status_display(status):
    """
    Возвращает человекочитаемое название статуса заказа с иконкой
    """
    status_display = {
        'pending': '⏳ Ожидает обработки',
        'confirmed': '✅ Подтвержден',
        'processing': '🔄 В обработке',
        'shipped': '🚚 Отправлен',
        'delivered': '📦 Доставлен',
        'cancelled': '❌ Отменен',
        'returned': '↩️ Возвращен',
    }
    return status_display.get(status, status)


def can_cancel_order(order, user=None):
    """
    Проверяет, можно ли отменить заказ
    """
    # Заказ может отменить только его создатель
    if user and order.user != user:
        return False
    
    # Заказ можно отменить только в определенных статусах
    cancellable_statuses = ['pending', 'confirmed']
    if order.status not in cancellable_statuses:
        return False
    
    # Нельзя отменить оплаченный заказ (требует дополнительных процедур)
    if order.is_paid:
        return False
    
    return True


def get_delivery_time_estimate(delivery_method, city=None):
    """
    Возвращает примерное время доставки
    """
    estimates = {
        'pickup': 'Готов к самовывозу в течение 1-2 рабочих дней',
        'delivery': 'Доставка в течение 1-3 рабочих дней',
        'transport_company': 'Доставка транспортной компанией в течение 3-7 рабочих дней',
    }
    
    base_estimate = estimates.get(delivery_method, 'Срок доставки уточняется')
    
    # Можно добавить логику для разных городов
    if city and city.lower() not in ['минск', 'гомель']:
        if delivery_method == 'delivery':
            base_estimate = 'Доставка в другие города в течение 5-10 рабочих дней'
    
    return base_estimate


def create_order_analytics_data(order):
    """
    Создает данные для аналитики заказа
    """
    analytics_data = {
        'order_id': order.id,
        'order_number': order.number,
        'user_id': order.user.id if order.user else None,
        'customer_type': 'company' if order.company_name else 'individual',
        'delivery_method': order.delivery_method,
        'payment_method': order.payment_method,
        'total_amount': float(order.total_amount),
        'items_count': order.items.count(),
        'created_at': order.created_at.isoformat(),
        'source': 'website',
    }
    
    # Добавляем информацию о товарах
    categories = set()
    for item in order.items.all():
        if hasattr(item.product, 'category') and item.product.category:
            categories.add(item.product.category.name)
    
    analytics_data['categories'] = list(categories)
    
    return analytics_data