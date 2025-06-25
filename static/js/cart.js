// static/js/cart.js
// Функциональность корзины для сайта ОАО "ГЗЛиН"

class Cart {
    constructor() {
        this.items = this.loadCart();
        this.init();
        this.updateCartUI();
    }

    init() {
        // Обновляем счетчик при загрузке страницы
        document.addEventListener('DOMContentLoaded', () => {
            this.updateCartCount();
            this.bindEvents();
        });
    }

    bindEvents() {
        // Привязываем события к кнопкам "Добавить в корзину"
        document.querySelectorAll('.add-to-cart-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const productId = button.dataset.productId;
                const productName = button.dataset.productName;
                const productPrice = parseFloat(button.dataset.productPrice);
                const productImage = button.dataset.productImage;
                
                this.addToCart(productId, productName, productPrice, productImage, button);
            });
        });

        // Кнопки изменения количества
        document.querySelectorAll('.quantity-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const action = button.dataset.action;
                const productId = button.dataset.productId;
                
                if (action === 'increase') {
                    this.increaseQuantity(productId);
                } else if (action === 'decrease') {
                    this.decreaseQuantity(productId);
                }
            });
        });

        // Удаление товара из корзины
        document.querySelectorAll('.remove-from-cart').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const productId = button.dataset.productId;
                this.removeFromCart(productId);
            });
        });

        // Управление выпадающим меню пользователя
        const userMenuToggle = document.querySelector('.user-menu-toggle');
        if (userMenuToggle) {
            userMenuToggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleUserMenu();
            });
        }

        // Закрытие выпадающего меню при клике вне его
        document.addEventListener('click', (e) => {
            const dropdown = document.querySelector('.dropdown');
            if (dropdown && !dropdown.contains(e.target)) {
                this.closeUserMenu();
            }
        });
    }

    addToCart(productId, productName, productPrice, productImage, button) {
        // Анимация кнопки
        this.animateButton(button, 'adding');
        
        // Проверяем, есть ли товар уже в корзине
        const existingItem = this.items.find(item => item.id === productId);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.items.push({
                id: productId,
                name: productName,
                price: productPrice,
                image: productImage,
                quantity: 1
            });
        }

        // Сохраняем корзину
        this.saveCart();
        
        // Обновляем UI
        this.updateCartUI();
        
        // Показываем уведомление
        this.showNotification(`${productName} добавлен в корзину`, 'success');
        
        // Анимация успеха для кнопки
        setTimeout(() => {
            this.animateButton(button, 'success');
            setTimeout(() => {
                this.resetButton(button);
            }, 2000);
        }, 800);
    }

    increaseQuantity(productId) {
        const item = this.items.find(item => item.id === productId);
        if (item) {
            item.quantity += 1;
            this.saveCart();
            this.updateCartUI();
            this.updateCartPage();
        }
    }

    decreaseQuantity(productId) {
        const item = this.items.find(item => item.id === productId);
        if (item && item.quantity > 1) {
            item.quantity -= 1;
            this.saveCart();
            this.updateCartUI();
            this.updateCartPage();
        } else if (item && item.quantity === 1) {
            this.removeFromCart(productId);
        }
    }

    removeFromCart(productId) {
        this.items = this.items.filter(item => item.id !== productId);
        this.saveCart();
        this.updateCartUI();
        this.updateCartPage();
        this.showNotification('Товар удален из корзины', 'info');
    }

    updateCartCount() {
        const cartCount = document.getElementById('cartCount');
        const cartCountMobile = document.getElementById('cartCountMobile');
        const totalItems = this.items.reduce((sum, item) => sum + item.quantity, 0);
        
        if (cartCount) {
            cartCount.textContent = totalItems;
            cartCount.style.display = totalItems > 0 ? 'flex' : 'none';
        }
        
        if (cartCountMobile) {
            cartCountMobile.textContent = totalItems;
            cartCountMobile.style.display = totalItems > 0 ? 'flex' : 'none';
        }
    }

    updateCartUI() {
        this.updateCartCount();
        // Добавим другие обновления UI при необходимости
    }

    updateCartPage() {
        // Обновляем страницу корзины, если мы на ней находимся
        const cartPage = document.querySelector('.cart-page');
        if (cartPage) {
            this.renderCartItems();
            this.updateCartTotal();
        }
    }

    renderCartItems() {
        const cartItemsContainer = document.querySelector('.cart-items');
        if (!cartItemsContainer) return;

        if (this.items.length === 0) {
            cartItemsContainer.innerHTML = `
                <div class="empty-cart" style="text-align: center; padding: 3rem; color: var(--secondary-gray);">
                    <i class="fas fa-shopping-cart" style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                    <h3>Корзина пуста</h3>
                    <p>Добавьте товары из каталога</p>
                    <a href="/catalog/" class="btn btn-primary">Перейти в каталог</a>
                </div>
            `;
            return;
        }

        cartItemsContainer.innerHTML = this.items.map(item => `
            <div class="cart-item" data-product-id="${item.id}" style="display: grid; grid-template-columns: 80px 1fr 120px 120px 120px 80px; gap: 1rem; padding: 1.5rem; border-bottom: 1px solid var(--light-gray); align-items: center;">
                <div class="item-image">
                    <img src="${item.image || '/static/images/no-image.png'}" alt="${item.name}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 5px;">
                </div>
                <div class="item-info">
                    <h4 style="margin-bottom: 0.5rem; color: var(--primary-red);">${item.name}</h4>
                    <small style="color: var(--secondary-gray);">Артикул: ${item.id}</small>
                </div>
                <div class="item-price">
                    <strong>${this.formatPrice(item.price)} BYN</strong>
                </div>
                <div class="quantity-controls">
                    <button class="quantity-btn" data-action="decrease" data-product-id="${item.id}">-</button>
                    <input type="number" value="${item.quantity}" min="1" class="quantity-input" readonly>
                    <button class="quantity-btn" data-action="increase" data-product-id="${item.id}">+</button>
                </div>
                <div class="item-total">
                    <strong>${this.formatPrice(item.price * item.quantity)} BYN</strong>
                </div>
                <div class="item-actions">
                    <button class="remove-from-cart" data-product-id="${item.id}" style="background: none; border: none; color: var(--primary-red); font-size: 1.2rem; cursor: pointer;" title="Удалить">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');

        // Перепривязываем события после рендера
        this.bindEvents();
    }

    updateCartTotal() {
        const cartTotal = document.querySelector('.cart-total');
        if (!cartTotal) return;

        const total = this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const itemsCount = this.items.reduce((sum, item) => sum + item.quantity, 0);

        cartTotal.innerHTML = `
            <div style="text-align: right; padding: 2rem; background: var(--light-gray); border-radius: 10px;">
                <div style="margin-bottom: 0.5rem;">
                    <span>Товаров: ${itemsCount} шт.</span>
                </div>
                <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary-red);">
                    Итого: ${this.formatPrice(total)} BYN
                </div>
                <button class="btn btn-primary" style="margin-top: 1rem; width: 100%;">
                    Оформить заказ
                </button>
            </div>
        `;
    }

    animateButton(button, state) {
        button.classList.remove('adding', 'success', 'error');
        
        switch (state) {
            case 'adding':
                button.classList.add('adding');
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Добавляем...';
                button.disabled = true;
                break;
            case 'success':
                button.classList.add('success');
                button.innerHTML = '<i class="fas fa-check"></i> Добавлено';
                break;
            case 'error':
                button.classList.add('error');
                button.innerHTML = '<i class="fas fa-exclamation"></i> Ошибка';
                break;
        }
    }

    resetButton(button) {
        button.classList.remove('adding', 'success', 'error');
        button.innerHTML = '<i class="fas fa-shopping-cart"></i> В корзину';
        button.disabled = false;
    }

    toggleUserMenu() {
        const dropdown = document.querySelector('.dropdown-menu');
        if (dropdown) {
            dropdown.classList.toggle('active');
        }
    }

    closeUserMenu() {
        const dropdown = document.querySelector('.dropdown-menu');
        if (dropdown) {
            dropdown.classList.remove('active');
        }
    }

    showNotification(message, type = 'info') {
        // Удаляем существующие уведомления
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => notification.remove());

        // Создаем новое уведомление
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: inherit; font-size: 1.2rem; cursor: pointer; margin-left: 1rem;">×</button>
            </div>
        `;

        document.body.appendChild(notification);

        // Автоматически удаляем через 3 секунды
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    formatPrice(price) {
        return new Intl.NumberFormat('ru-RU', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(price);
    }

    saveCart() {
        try {
            const cartData = JSON.stringify(this.items);
            localStorage.setItem('gzlin_cart', cartData);
        } catch (error) {
            console.warn('Не удалось сохранить корзину в localStorage:', error);
        }
    }

    loadCart() {
        try {
            const cartData = localStorage.getItem('gzlin_cart');
            return cartData ? JSON.parse(cartData) : [];
        } catch (error) {
            console.warn('Не удалось загрузить корзину из localStorage:', error);
            return [];
        }
    }

    clearCart() {
        this.items = [];
        this.saveCart();
        this.updateCartUI();
        this.updateCartPage();
        this.showNotification('Корзина очищена', 'info');
    }

    getCartTotal() {
        return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    }

    getCartItemsCount() {
        return this.items.reduce((sum, item) => sum + item.quantity, 0);
    }
}

// Инициализируем корзину
const cart = new Cart();

// Экспортируем для использования в других скриптах
window.GZLinCart = cart;