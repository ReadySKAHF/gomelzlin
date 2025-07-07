/**
 * Wishlist functionality for ОАО "ГЗЛиН" website
 * Функционал избранного для сайта ОАО "ГЗЛиН"
 */

class WishlistManager {
    constructor() {
        this.wishlistItems = new Set();
        this.init();
    }

    // Инициализация
    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initWishlistButtons();
            this.loadWishlistFromServer();
        });
    }

    // Инициализация кнопок избранного на странице
    initWishlistButtons() {
        const wishlistBtns = document.querySelectorAll('.wishlist-btn, .wishlist-btn-detail');
        
        wishlistBtns.forEach(btn => {
            const productId = btn.getAttribute('data-product-id');
            if (productId) {
                this.checkWishlistStatus(productId);
                
                // Добавляем обработчик события, если он еще не добавлен
                if (!btn.hasAttribute('data-wishlist-initialized')) {
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        const productName = btn.getAttribute('data-product-name') || 'товар';
                        this.toggleWishlist(productId, productName);
                    });
                    btn.setAttribute('data-wishlist-initialized', 'true');
                }
            }
        });
    }

    // Загрузка списка избранного с сервера
    loadWishlistFromServer() {
        if (!this.isUserLoggedIn()) {
            return;
        }

        fetch('/cart/wishlist/count/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.updateWishlistCounter(data.count);
                }
            })
            .catch(error => console.error('Error loading wishlist count:', error));
    }

    // Проверка статуса товара в избранном
    checkWishlistStatus(productId) {
        if (!this.isUserLoggedIn()) {
            return;
        }
        
        fetch(`/cart/wishlist/status/?product_id=${productId}`)
            .then(response => response.json())
            .then(data => {
                this.updateWishlistButton(productId, data.in_wishlist);
                if (data.in_wishlist) {
                    this.wishlistItems.add(productId.toString());
                }
            })
            .catch(error => console.error('Error checking wishlist status:', error));
    }

    // Переключение товара в избранном (добавить/удалить)
    toggleWishlist(productId, productName = 'товар') {
        // Проверяем авторизацию
        if (!this.isUserLoggedIn()) {
            this.showNotification('Для добавления в избранное необходимо войти в систему', 'warning');
            return;
        }
        
        const isInWishlist = this.wishlistItems.has(productId.toString());
        const action = isInWishlist ? 'remove' : 'add';
        
        // Временно обновляем UI для мгновенной обратной связи
        this.updateWishlistButton(productId, !isInWishlist);
        
        // Отправляем запрос на сервер
        fetch(`/cart/wishlist/${action}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: `product_id=${productId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (action === 'add') {
                    this.wishlistItems.add(productId.toString());
                    this.showNotification(data.message || `"${productName}" добавлен в избранное!`, 'success');
                } else {
                    this.wishlistItems.delete(productId.toString());
                    this.showNotification(data.message || `"${productName}" удален из избранного`, 'success');
                }
                
                // Обновляем счетчик в header
                this.updateWishlistCounter(data.wishlist_count);
            } else {
                // Возвращаем исходное состояние при ошибке
                this.updateWishlistButton(productId, isInWishlist);
                this.showNotification(data.message || 'Произошла ошибка', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Возвращаем исходное состояние при ошибке
            this.updateWishlistButton(productId, isInWishlist);
            this.showNotification('Произошла ошибка при работе с избранным', 'error');
        });
    }

    // Удаление товара из избранного (используется в профиле)
    removeFromWishlist(productId, productName = 'товар') {
        if (!this.isUserLoggedIn()) {
            this.showNotification('Необходимо войти в систему', 'warning');
            return;
        }

        fetch('/cart/wishlist/remove/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: `product_id=${productId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.wishlistItems.delete(productId.toString());
                this.showNotification(data.message || `"${productName}" удален из избранного`, 'success');
                
                // Удаляем элемент из DOM если он есть (для страницы профиля)
                const wishlistItem = document.querySelector(`.wishlist-item[data-product-id="${productId}"]`);
                if (wishlistItem) {
                    wishlistItem.style.animation = 'fadeOut 0.3s ease';
                    setTimeout(() => {
                        wishlistItem.remove();
                        
                        // Проверяем, остались ли товары в избранном
                        const remainingItems = document.querySelectorAll('.wishlist-item');
                        if (remainingItems.length === 0) {
                            this.showEmptyWishlistMessage();
                        }
                    }, 300);
                }
                
                // Обновляем все кнопки с этим товаром
                this.updateWishlistButton(productId, false);
                this.updateWishlistCounter(data.wishlist_count);
            } else {
                this.showNotification(data.message || 'Произошла ошибка', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('Произошла ошибка при удалении товара', 'error');
        });
    }

    // Обновление внешнего вида кнопки избранного
    updateWishlistButton(productId, isInWishlist) {
        const buttons = document.querySelectorAll(`[data-product-id="${productId}"]`);
        
        buttons.forEach(btn => {
            if (!btn.classList.contains('wishlist-btn') && !btn.classList.contains('wishlist-btn-detail')) {
                return; // Пропускаем элементы, которые не являются кнопками избранного
            }

            const heartIcon = btn.querySelector('.heart-icon');
            const wishlistText = btn.querySelector('.wishlist-text');
            
            if (isInWishlist) {
                // Товар в избранном
                if (heartIcon) {
                    heartIcon.style.color = '#e74c3c';
                    heartIcon.textContent = '♥'; // Закрашенное сердце
                }
                
                btn.classList.add('in-wishlist');
                
                if (wishlistText) {
                    wishlistText.textContent = 'В избранном';
                }
                btn.title = 'Удалить из избранного';
                
                // Анимация добавления
                this.animateButton(btn, 'heartBeat');
                
            } else {
                // Товара нет в избранном
                if (heartIcon) {
                    heartIcon.style.color = btn.classList.contains('wishlist-btn-detail') ? 'var(--primary-red)' : '#ccc';
                    heartIcon.textContent = '♡'; // Пустое сердце
                }
                
                btn.classList.remove('in-wishlist');
                
                if (wishlistText) {
                    wishlistText.textContent = 'В избранное';
                }
                btn.title = 'Добавить в избранное';
            }
        });
    }

    // Обновление счетчика избранного в шапке
    updateWishlistCounter(count) {
        const counter = document.querySelector('.wishlist-counter');
        if (counter) {
            counter.textContent = count;
            counter.style.display = count > 0 ? 'inline-block' : 'none';
            
            // Анимация изменения счетчика
            if (count > 0) {
                this.animateButton(counter, 'bounce');
            }
        }
    }

    // Показ сообщения о пустом списке избранного
    showEmptyWishlistMessage() {
        const wishlistContainer = document.querySelector('.wishlist-content');
        if (wishlistContainer) {
            wishlistContainer.innerHTML = `
                <div style="text-align: center; padding: 3rem 0; color: #666;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">💝</div>
                    <h3>Ваш список избранного пуст</h3>
                    <p>Добавляйте товары в избранное, чтобы не потерять их!</p>
                    <a href="/catalog/" style="background: #cb413b; color: white; padding: 1rem 2rem; border-radius: 8px; text-decoration: none; display: inline-block; margin-top: 1rem;">
                        Перейти к каталогу
                    </a>
                </div>
            `;
        }
    }

    // Анимация кнопки
    animateButton(element, animationType) {
        element.style.animation = `${animationType} 0.6s ease`;
        setTimeout(() => {
            element.style.animation = '';
        }, 600);
    }

    // Проверка авторизации пользователя
    isUserLoggedIn() {
        return document.querySelector('[name=csrfmiddlewaretoken]') !== null || 
               document.querySelector('meta[name="csrf-token"]') !== null ||
               document.body.dataset.userAuthenticated === 'true';
    }

    // Получение CSRF токена
    getCSRFToken() {
        // Из скрытого поля формы
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) return token.value;
        
        // Из meta тега
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) return metaToken.getAttribute('content');
        
        // Из cookie (если используется)
        const cookieToken = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        if (cookieToken) return cookieToken.split('=')[1];
        
        return '';
    }

    showNotification(text, type = 'info') {
    const existingNotifications = document.querySelectorAll('.wishlist-notification');
    existingNotifications.forEach(notification => notification.remove());

    const notification = document.createElement('div');
    notification.className = 'wishlist-notification';
    
    const colors = {
        success: '#4CAF50',
        error: '#f44336',
        info: '#2196F3',
        warning: '#ff9800'
    };
    
    const icons = {
        success: '♥️',
        error: '❌', 
        info: '💙',
        warning: '⚠️'
    };
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        z-index: 10001;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        font-weight: 500;
        max-width: 350px;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        border-left: 4px solid rgba(255, 255, 255, 0.3);
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
    }, 4000);
    }

    // Скрытие уведомления
    hideNotification(notification) {
        if (notification && document.body.contains(notification)) {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }
    }

    // Получение цвета уведомления в зависимости от типа
    getNotificationColor(type) {
        const colors = {
            'success': '#28a745',
            'error': '#dc3545',
            'warning': '#ffc107',
            'info': '#cb413b'
        };
        return colors[type] || colors.info;
    }

    // Добавление товара в корзину (дополнительная функция)
    addToCart(productId, productName = 'товар', price = null) {
        if (!productId) {
            this.showNotification('Ошибка: не указан товар', 'error');
            return;
        }

        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: `product_id=${productId}&quantity=1`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification(data.message || `"${productName}" добавлен в корзину!`, 'success');
                this.updateCartCounter(data.cart_count);
            } else {
                this.showNotification(data.message || 'Ошибка добавления товара', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('Произошла ошибка при добавлении товара', 'error');
        });
    }

    // Обновление счетчика корзины
    updateCartCounter(count) {
        const counter = document.querySelector('.cart-counter');
        if (counter) {
            counter.textContent = count;
            counter.style.display = count > 0 ? 'inline-block' : 'none';
        }
    }
}

// Создаем глобальный экземпляр менеджера избранного
const wishlistManager = new WishlistManager();

// Глобальные функции для обратной совместимости
function toggleWishlist(productId, productName) {
    wishlistManager.toggleWishlist(productId, productName);
}

function removeFromWishlist(productId, productName) {
    wishlistManager.removeFromWishlist(productId, productName);
}

function addToCart(productId, productName, price) {
    wishlistManager.addToCart(productId, productName, price);
}

// Экспорт для использования в модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WishlistManager;
}