// static/js/cart.js
// Исправленный модуль корзины для ОАО "ГЗЛиН"

class CartManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateCartCount();
        this.initializeCartUI();
    }

    bindEvents() {
        // Обработчики для кнопок изменения количества
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quantity-btn')) {
                const itemId = e.target.dataset.itemId;
                const change = e.target.dataset.change;
                this.updateQuantity(e.target, itemId, change);
            }

            // Обработчик для кнопок удаления товара
            if (e.target.classList.contains('remove-item-btn')) {
                const itemId = e.target.dataset.itemId;
                this.removeItem(e.target, itemId);
            }

            // Обработчик для кнопки очистки корзины
            if (e.target.classList.contains('clear-cart-btn')) {
                this.clearCart();
            }
        });

        // Обработчики для прямого ввода количества
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('quantity-input')) {
                this.updateQuantityInput(e.target);
            }
        });

        // Предотвращение отправки формы при нажатии Enter в поле количества
        document.addEventListener('keypress', (e) => {
            if (e.target.classList.contains('quantity-input') && e.key === 'Enter') {
                e.preventDefault();
                this.updateQuantityInput(e.target);
            }
        });
    }

    async addToCart(productId, productName = '', productPrice = 0, quantity = 1) {
        if (!productId) {
            this.showMessage('Ошибка: не указан товар', 'error');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('quantity', quantity);  // ← ИСПРАВЛЕНО!

            const response = await fetch('/cart/add/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                this.updateCartCount(data.cart_count);
                const message = quantity === 1 ? 
                    `${productName} добавлен в корзину` : 
                    `${productName} добавлен в корзину (${quantity} шт.)`;
                this.showMessage(data.message || message, 'success');
                
                // Обновляем интерфейс корзины если находимся на странице корзины
                if (window.location.pathname.includes('/cart/')) {
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                }
            } else {
                this.showMessage(data.message || 'Ошибка при добавлении товара', 'error');
            }
        } catch (error) {
            this.showMessage('Произошла ошибка при добавлении товара', 'error');
            console.error('Add to cart error:', error);
        }
    }

    async updateQuantity(button, itemId, change) {
        if (!itemId || !change) {
            this.showMessage('Ошибка: неверные параметры', 'error');
            return;
        }

        try {
            this.setLoading(button, true);

            const formData = new FormData();
            formData.append('item_id', itemId);
            formData.append('change', change);

            const response = await fetch('/cart/update/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                if (data.item_deleted) {
                    // Удаляем строку товара из DOM
                    const cartItem = button.closest('.cart-item');
                    if (cartItem) {
                        this.animateRemoval(cartItem);
                    }
                } else {
                    // Обновляем количество и цены
                    this.updateCartItemUI(itemId, data);
                }

                this.updateCartCount(data.cart_count);
                this.updateCartTotal(data.cart_total);
                this.showMessage(data.message, 'success');
            } else {
                this.showMessage(data.message || 'Ошибка при обновлении корзины', 'error');
            }
        } catch (error) {
            this.showMessage('Произошла ошибка при обновлении корзины', 'error');
            console.error('Cart update error:', error);
        } finally {
            this.setLoading(button, false);
        }
    }

    async updateQuantityInput(input) {
        const itemId = input.dataset.itemId;
        const quantity = parseInt(input.value);
        const prevValue = parseInt(input.dataset.prevValue) || 1;

        if (!itemId) {
            this.showMessage('Ошибка: не указан товар', 'error');
            return;
        }

        if (quantity < 1) {
            input.value = 1;
            this.showMessage('Количество не может быть меньше 1', 'error');
            return;
        }

        if (quantity === prevValue) {
            return; // Значение не изменилось
        }

        try {
            const formData = new FormData();
            formData.append('item_id', itemId);
            formData.append('quantity', quantity);

            const response = await fetch('/cart/update-quantity/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                this.updateCartItemUI(itemId, data);
                this.updateCartCount(data.cart_count);
                this.updateCartTotal(data.cart_total);
                input.dataset.prevValue = quantity;
                this.showMessage(data.message, 'success');
            } else {
                input.value = prevValue; // Возвращаем предыдущее значение
                this.showMessage(data.message || 'Ошибка при обновлении количества', 'error');
            }
        } catch (error) {
            input.value = prevValue;
            this.showMessage('Произошла ошибка при обновлении количества', 'error');
            console.error('Quantity update error:', error);
        }
    }

    async removeItem(button, itemId) {
        if (!itemId) {
            this.showMessage('Ошибка: не указан товар', 'error');
            return;
        }

        if (!confirm('Удалить товар из корзины?')) {
            return;
        }

        try {
            this.setLoading(button, true);

            const formData = new FormData();
            formData.append('item_id', itemId);

            const response = await fetch('/cart/remove/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                // Удаляем элемент из DOM с анимацией
                const cartItem = button.closest('.cart-item');
                if (cartItem) {
                    this.animateRemoval(cartItem);
                }

                this.updateCartCount(data.cart_count);
                this.updateCartTotal(data.cart_total);
                this.showMessage(data.message, 'success');
                
                // Проверяем, не стала ли корзина пустой
                setTimeout(() => {
                    this.checkEmptyCart();
                }, 300);
            } else {
                this.showMessage(data.message || 'Ошибка при удалении товара', 'error');
            }
        } catch (error) {
            this.showMessage('Произошла ошибка при удалении товара', 'error');
            console.error('Remove item error:', error);
        } finally {
            this.setLoading(button, false);
        }
    }

    updateCartItemUI(itemId, data) {
        const cartItem = document.querySelector(`[data-item-id="${itemId}"]`)?.closest('.cart-item');
        
        if (cartItem) {
            // Обновляем количество
            const quantityInput = cartItem.querySelector('.quantity-input');
            if (quantityInput && data.item_quantity !== undefined) {
                quantityInput.value = data.item_quantity;
                quantityInput.dataset.prevValue = data.item_quantity;
            }

            // Обновляем общую стоимость товара
            const itemTotal = cartItem.querySelector('.item-total');
            if (itemTotal && data.item_total !== undefined) {
                itemTotal.textContent = `${data.item_total} BYN`;
            }
        }
    }

    updateCartCount(count) {
        const cartCountElements = document.querySelectorAll('.cart-count, #cartCount');
        cartCountElements.forEach(element => {
            if (element) {
                element.textContent = count || 0;
            }
        });
    }

    updateCartTotal(total) {
        const cartTotalElements = document.querySelectorAll('.cart-total, #cartTotal');
        cartTotalElements.forEach(element => {
            if (element) {
                element.textContent = `${total || 0} BYN`;
            }
        });
    }

    checkEmptyCart() {
        const cartItems = document.querySelectorAll('.cart-item');
        if (cartItems.length === 0) {
            const cartContent = document.getElementById('cartContent');
            if (cartContent) {
                cartContent.innerHTML = `
                    <div class="empty-cart-message" style="text-align: center; padding: 3rem; color: var(--secondary-gray);">
                        <h2>Корзина пуста</h2>
                        <p style="margin: 1rem 0;">Добавьте товары в корзину, чтобы оформить заказ</p>
                        <a href="/catalog/" class="btn btn-primary">Перейти к каталогу</a>
                    </div>
                `;
            }
        }
    }

    animateRemoval(element) {
        element.style.transition = 'opacity 0.3s, transform 0.3s';
        element.style.opacity = '0';
        element.style.transform = 'translateX(-100%)';
        
        setTimeout(() => {
            element.remove();
        }, 300);
    }

    setLoading(button, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.style.opacity = '0.6';
            button.style.cursor = 'not-allowed';
        } else {
            button.disabled = false;
            button.style.opacity = '1';
            button.style.cursor = 'pointer';
        }
    }

    showMessage(message, type = 'info') {
        // Удаляем предыдущие уведомления
        const existingMessages = document.querySelectorAll('.cart-notification');
        existingMessages.forEach(msg => msg.remove());

        const notification = document.createElement('div');
        notification.className = 'cart-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 2rem;
            border-radius: 8px;
            color: white;
            z-index: 1001;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideInRight 0.3s ease;
        `;
        
        // Цвета для разных типов сообщений
        switch (type) {
            case 'success':
                notification.style.background = '#28a745';
                break;
            case 'error':
                notification.style.background = '#dc3545';
                break;
            case 'warning':
                notification.style.background = '#ffc107';
                notification.style.color = '#000';
                break;
            default:
                notification.style.background = '#cb413b';
        }
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Автоматическое удаление через 3 секунды
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }
        }, 3000);
    }

    getCSRFToken() {
        // Пытаемся получить CSRF токен из разных источников
        let token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        if (!token) {
            token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        }
        
        if (!token) {
            // Пытаемся получить из cookies
            const name = 'csrftoken';
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            token = cookieValue;
        }
        
        return token;
    }

    initializeCartUI() {
        // Инициализация интерфейса корзины
        this.addAnimationStyles();
        
        // Загружаем текущее состояние корзины
        this.loadCartState();
    }

    addAnimationStyles() {
        if (!document.getElementById('cart-animations')) {
            const style = document.createElement('style');
            style.id = 'cart-animations';
            style.textContent = `
                @keyframes slideInRight {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                
                @keyframes slideOutRight {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }
                
                .cart-item {
                    transition: all 0.3s ease;
                }
                
                .cart-item:hover {
                    background-color: var(--light-gray, #f8f9fa);
                }
                
                .quantity-btn {
                    transition: all 0.2s ease;
                }
                
                .quantity-btn:hover:not(:disabled) {
                    transform: scale(1.1);
                    background-color: var(--primary-red, #cb413b);
                    color: white;
                }
                
                .quantity-input {
                    transition: border-color 0.2s ease;
                }
                
                .quantity-input:focus {
                    outline: none;
                    border-color: var(--primary-red, #cb413b);
                    box-shadow: 0 0 0 2px rgba(203, 65, 59, 0.2);
                }
            `;
            document.head.appendChild(style);
        }
    }

    async loadCartState() {
        try {
            const response = await fetch('/cart/count/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateCartCount(data.cart_count);
            }
        } catch (error) {
            console.log('Не удалось загрузить состояние корзины:', error);
        }
    }

    async clearCart() {
        this.showClearCartAlert();
    }

    showClearCartAlert() {
    if (!document.getElementById('clearCartAlert')) {
        const alertHTML = `
            <div id="clearCartAlert" class="custom-alert-overlay">
                <div class="custom-alert">
                    <div class="custom-alert-header">
                        <span class="custom-alert-icon">🗑️</span>
                        <h3 class="custom-alert-title">Очистить корзину?</h3>
                    </div>
                    <div class="custom-alert-body">
                        <p class="custom-alert-message">Вы уверены, что хотите удалить все товары из корзины?</p>
                        <p class="custom-alert-submessage">Это действие нельзя будет отменить</p>
                        <div class="custom-alert-actions">
                            <button class="custom-alert-btn cancel" onclick="window.cartManager.hideClearCartAlert()">
                                Отмена
                            </button>
                            <button class="custom-alert-btn confirm" onclick="window.cartManager.confirmClearCart()">
                                Очистить
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', alertHTML);
    }

    const alertOverlay = document.getElementById('clearCartAlert');
    alertOverlay.classList.add('show');
    
    document.body.style.overflow = 'hidden';
    
    this.handleEscapeKey = (e) => {
        if (e.key === 'Escape') {
            this.hideClearCartAlert();
        }
    };
    document.addEventListener('keydown', this.handleEscapeKey);
    
    alertOverlay.addEventListener('click', (e) => {
        if (e.target === alertOverlay) {
            this.hideClearCartAlert();
        }
    });
}

hideClearCartAlert() {
    const alertOverlay = document.getElementById('clearCartAlert');
    if (alertOverlay) {
        alertOverlay.classList.remove('show');
    }
    
    document.body.style.overflow = '';
    
    if (this.handleEscapeKey) {
        document.removeEventListener('keydown', this.handleEscapeKey);
        this.handleEscapeKey = null;
    }
}
async confirmClearCart() {
    this.hideClearCartAlert();
    
    try {
        const response = await fetch('/cart/clear/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        });

        const data = await response.json();

        if (data.success) {
            const cartItems = document.querySelectorAll('.cart-item');
            cartItems.forEach(item => this.animateRemoval(item));

            this.updateCartCount(0);
            this.updateCartTotal(0);
            this.showSuccessMessage('Корзина успешно очищена');
            
            setTimeout(() => {
                this.checkEmptyCart();
            }, 300);
        } else {
            this.showMessage(data.message || 'Ошибка при очистке корзины', 'error');
        }
    } catch (error) {
        this.showMessage('Произошла ошибка при очистке корзины', 'error');
        console.error('Clear cart error:', error);
    }
}

showSuccessMessage(text) {
    this.showNotification(text, 'success');
}
showNotification(text, type = 'info') {
    const existingNotifications = document.querySelectorAll('.cart-notification');
    existingNotifications.forEach(notification => notification.remove());

    const notification = document.createElement('div');
    notification.className = 'cart-notification';
    
    const colors = {
        success: '#4CAF50',
        error: '#f44336',
        info: '#2196F3',
        warning: '#ff9800'
    };
    
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️',
        warning: '⚠️'
    };
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        z-index: 10001;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        font-weight: 500;
        max-width: 300px;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    `;
    
    notification.innerHTML = `${icons[type]} ${text}`;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}
}

// Глобальные функции для совместимости с существующим кодом
window.addToCart = function(productId, productName = '', productPrice = 0) {
    if (window.cartManager) {
        window.cartManager.addToCart(productId, productName, productPrice);
    } else {
        console.error('Cart manager не инициализирован');
    }
};

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    window.cartManager = new CartManager();
    
    // Обновляем счетчик корзины при загрузке страницы
    const cartCountElement = document.getElementById('cartCount');
    if (cartCountElement && !cartCountElement.textContent) {
        cartCountElement.textContent = '0';
    }
});

// Экспорт для использования в модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CartManager;
}

