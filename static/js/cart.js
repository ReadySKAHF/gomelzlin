// Корзина - JavaScript функционал
class Cart {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateCartCount();
    }

    bindEvents() {
        // Добавление товара в корзину
        document.addEventListener('click', (e) => {
            if (e.target.closest('.add-to-cart-btn')) {
                e.preventDefault();
                this.addToCart(e.target.closest('.add-to-cart-btn'));
            }
        });

        // Обновление количества в корзине
        document.addEventListener('click', (e) => {
            if (e.target.closest('.quantity-btn')) {
                e.preventDefault();
                this.updateQuantity(e.target.closest('.quantity-btn'));
            }
        });

        // Удаление товара из корзины
        document.addEventListener('click', (e) => {
            if (e.target.closest('.remove-item-btn')) {
                e.preventDefault();
                this.removeItem(e.target.closest('.remove-item-btn'));
            }
        });

        // Очистка корзины
        document.addEventListener('click', (e) => {
            if (e.target.closest('.clear-cart-btn')) {
                e.preventDefault();
                this.clearCart();
            }
        });

        // Обновление количества через input
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('quantity-input')) {
                this.updateQuantityInput(e.target);
            }
        });
    }

    async addToCart(button) {
        const productId = button.dataset.productId;
        const quantity = parseInt(button.dataset.quantity || 1);

        if (!productId) {
            this.showMessage('Ошибка: не указан товар', 'error');
            return;
        }

        try {
            this.setLoading(button, true);

            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('quantity', quantity);

            const response = await fetch('/cart/add/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage(data.message, 'success');
                this.updateCartCount(data.cart_count);
                this.animateCartIcon();
            } else {
                this.showMessage(data.message, 'error');
            }
        } catch (error) {
            this.showMessage('Произошла ошибка при добавлении товара', 'error');
            console.error('Cart error:', error);
        } finally {
            this.setLoading(button, false);
        }
    }

    async updateQuantity(button) {
        const itemId = button.dataset.itemId;
        const change = button.dataset.change;

        if (!itemId || !change) {
            this.showMessage('Ошибка: неверные параметры', 'error');
            return;
        }

        try {
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
                        cartItem.remove();
                    }
                } else {
                    // Обновляем количество и цены
                    this.updateCartItemUI(itemId, data);
                }

                this.updateCartCount(data.cart_count);
                this.updateCartTotal(data.cart_total);
                this.showMessage(data.message, 'success');
            } else {
                this.showMessage(data.message, 'error');
            }
        } catch (error) {
            this.showMessage('Произошла ошибка при обновлении корзины', 'error');
            console.error('Cart update error:', error);
        }
    }

    async updateQuantityInput(input) {
        const itemId = input.dataset.itemId;
        const quantity = parseInt(input.value);

        if (!itemId) {
            this.showMessage('Ошибка: не указан товар', 'error');
            return;
        }

        if (quantity < 0) {
            input.value = 1;
            return;
        }

        try {
            const formData = new FormData();
            formData.append('item_id', itemId);
            formData.append('quantity', quantity);

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
                    const cartItem = input.closest('.cart-item');
                    if (cartItem) {
                        cartItem.remove();
                    }
                } else {
                    this.updateCartItemUI(itemId, data);
                }

                this.updateCartCount(data.cart_count);
                this.updateCartTotal(data.cart_total);
            } else {
                this.showMessage(data.message, 'error');
                // Восстанавливаем предыдущее значение
                input.value = input.dataset.prevValue || 1;
            }
        } catch (error) {
            this.showMessage('Произошла ошибка при обновлении количества', 'error');
            input.value = input.dataset.prevValue || 1;
        }
    }

    async removeItem(button) {
        const itemId = button.dataset.itemId;

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
                    cartItem.style.transition = 'opacity 0.3s, transform 0.3s';
                    cartItem.style.opacity = '0';
                    cartItem.style.transform = 'translateX(-100%)';
                    
                    setTimeout(() => {
                        cartItem.remove();
                        this.checkEmptyCart();
                    }, 300);
                }

                this.updateCartCount(data.cart_count);
                this.updateCartTotal(data.cart_total);
                this.showMessage(data.message, 'success');
            } else {
                this.showMessage(data.message, 'error');
            }
        } catch (error) {
            this.showMessage('Произошла ошибка при удалении товара', 'error');
            console.error('Remove item error:', error);
        } finally {
            this.setLoading(button, false);
        }
    }

    async clearCart() {
        if (!confirm('Очистить корзину? Все товары будут удалены.')) {
            return;
        }

        try {
            const response = await fetch('/cart/clear/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                // Удаляем все товары из DOM
                const cartItems = document.querySelectorAll('.cart-item');
                cartItems.forEach(item => item.remove());

                this.updateCartCount(0);
                this.updateCartTotal(0);
                this.checkEmptyCart();
                this.showMessage(data.message, 'success');
            } else {
                this.showMessage(data.message, 'error');
            }
        } catch (error) {
            this.showMessage('Произошла ошибка при очистке корзины', 'error');
            console.error('Clear cart error:', error);
        }
    }

    updateCartItemUI(itemId, data) {
        const cartItem = document.querySelector(`[data-item-id="${itemId}"]`).closest('.cart-item');
        
        if (cartItem) {
            // Обновляем количество
            const quantityInput = cartItem.querySelector('.quantity-input');
            if (quantityInput) {
                quantityInput.value = data.new_quantity;
                quantityInput.dataset.prevValue = data.new_quantity;
            }

            // Обновляем цену за позицию
            const itemTotal = cartItem.querySelector('.item-total');
            if (itemTotal) {
                itemTotal.textContent = this.formatPrice(data.item_total);
            }
        }
    }

    updateCartCount(count) {
        const cartCountElements = document.querySelectorAll('.cart-count, #cartCount');
        cartCountElements.forEach(element => {
            element.textContent = count || 0;
            
            // Показываем/скрываем счетчик
            if (count > 0) {
                element.style.display = 'inline-block';
            } else {
                element.style.display = 'none';
            }
        });
    }

    updateCartTotal(total) {
        const cartTotalElements = document.querySelectorAll('.cart-total');
        cartTotalElements.forEach(element => {
            element.textContent = this.formatPrice(total);
        });
    }

    checkEmptyCart() {
        const cartItems = document.querySelectorAll('.cart-item');
        const emptyCartMessage = document.querySelector('.empty-cart-message');
        const cartContent = document.querySelector('.cart-content');

        if (cartItems.length === 0) {
            if (emptyCartMessage) {
                emptyCartMessage.style.display = 'block';
            }
            if (cartContent) {
                cartContent.style.display = 'none';
            }
        }
    }

    animateCartIcon() {
        const cartIcon = document.querySelector('.cart-link i');
        if (cartIcon) {
            cartIcon.style.animation = 'cartBounce 0.6s ease-in-out';
            setTimeout(() => {
                cartIcon.style.animation = '';
            }, 600);
        }
    }

    setLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Загрузка...';
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || button.innerHTML;
        }
    }

    showMessage(message, type = 'info') {
        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} cart-notification`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateX(400px);
            transition: transform 0.3s ease-in-out;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span>${message}</span>
                <button type="button" class="btn-close" onclick="this.closest('.cart-notification').remove()"></button>
            </div>
        `;

        document.body.appendChild(notification);

        // Анимация появления
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Автоматическое удаление через 5 секунд
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.transform = 'translateX(400px)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }

    formatPrice(price) {
        return new Intl.NumberFormat('ru-BY', {
            style: 'currency',
            currency: 'BYN',
            minimumFractionDigits: 2
        }).format(price);
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// CSS анимации
const style = document.createElement('style');
style.textContent = `
    @keyframes cartBounce {
        0%, 20%, 60%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-10px);
        }
        80% {
            transform: translateY(-5px);
        }
    }

    .cart-item {
        transition: all 0.3s ease;
    }

    .cart-item:hover {
        background-color: #f8f9fa;
    }

    .quantity-btn {
        transition: all 0.2s ease;
    }

    .quantity-btn:hover {
        transform: scale(1.1);
    }

    .cart-notification {
        animation: slideIn 0.3s ease-in-out;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(400px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    .btn-close {
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        opacity: 0.7;
        transition: opacity 0.2s;
    }

    .btn-close:hover {
        opacity: 1;
    }
`;
document.head.appendChild(style);

// Инициализация корзины при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new Cart();
});

// Экспорт для использования в других скриптах
window.Cart = Cart;