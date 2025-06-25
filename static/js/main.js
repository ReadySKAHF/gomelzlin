// static/js/main.js
// Основной JavaScript файл для сайта ОАО "ГЗЛиН"

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Инициализация всех компонентов
    initSearchAutocomplete();
    initCartFunctions();
    initMobileMenu();
    initScrollEffects();
    initTooltips();
    initLazyLoading();
}

// === ПОИСК И АВТОКОМПЛИТ ===
let searchTimeout;
let searchCache = new Map();

function initSearchAutocomplete() {
    const searchInputs = document.querySelectorAll('input[type="search"], input[placeholder*="Поиск"]');
    
    searchInputs.forEach(input => {
        const dropdown = createSearchDropdown(input);
        
        input.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(query, dropdown);
                }, 300);
            } else {
                hideSearchDropdown(dropdown);
            }
        });
        
        input.addEventListener('focus', function() {
            if (this.value.length >= 2) {
                const dropdown = this.nextElementSibling;
                if (dropdown && dropdown.classList.contains('search-dropdown')) {
                    dropdown.style.display = 'block';
                }
            }
        });
        
        // Скрывать при клике вне элемента
        document.addEventListener('click', function(e) {
            if (!input.contains(e.target)) {
                hideSearchDropdown(dropdown);
            }
        });
    });
}

function createSearchDropdown(input) {
    const dropdown = document.createElement('div');
    dropdown.className = 'search-dropdown';
    dropdown.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #e9ecef;
        border-top: none;
        border-radius: 0 0 8px 8px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        max-height: 300px;
        overflow-y: auto;
        z-index: 1000;
        display: none;
    `;
    
    input.parentElement.style.position = 'relative';
    input.parentElement.appendChild(dropdown);
    
    return dropdown;
}

async function performSearch(query, dropdown) {
    // Проверяем кэш
    if (searchCache.has(query)) {
        displaySearchResults(searchCache.get(query), dropdown);
        return;
    }
    
    try {
        const response = await fetch(`/catalog/ajax/search-suggestions/?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        // Кэшируем результат
        searchCache.set(query, data.suggestions);
        displaySearchResults(data.suggestions, dropdown);
    } catch (error) {
        console.error('Ошибка поиска:', error);
    }
}

function displaySearchResults(suggestions, dropdown) {
    if (!suggestions || suggestions.length === 0) {
        hideSearchDropdown(dropdown);
        return;
    }
    
    dropdown.innerHTML = '';
    
    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'search-result-item';
        item.style.cssText = `
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #f8f9fa;
            cursor: pointer;
            transition: background-color 0.2s ease;
        `;
        
        item.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <div class="fw-bold">${highlightQuery(suggestion.label, dropdown.previousElementSibling.value)}</div>
                    <small class="text-muted">${suggestion.category} • ${suggestion.price} BYN</small>
                </div>
                <i class="fas fa-arrow-right text-muted"></i>
            </div>
        `;
        
        item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'white';
        });
        
        item.addEventListener('click', function() {
            window.location.href = suggestion.url;
        });
        
        dropdown.appendChild(item);
    });
    
    dropdown.style.display = 'block';
}

function highlightQuery(text, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

function hideSearchDropdown(dropdown) {
    if (dropdown) {
        dropdown.style.display = 'none';
    }
}

// === КОРЗИНА ===
function initCartFunctions() {
    updateCartCounter();
    
    // Обработчики для кнопок корзины
    document.addEventListener('click', function(e) {
        if (e.target.closest('[data-action="add-to-cart"]')) {
            e.preventDefault();
            const button = e.target.closest('[data-action="add-to-cart"]');
            const productId = button.dataset.productId;
            const quantity = button.dataset.quantity || 1;
            
            addToCart(productId, quantity);
        }
        
        if (e.target.closest('[data-action="remove-from-cart"]')) {
            e.preventDefault();
            const button = e.target.closest('[data-action="remove-from-cart"]');
            const itemId = button.dataset.itemId;
            
            removeFromCart(itemId);
        }
    });
}

async function addToCart(productId, quantity = 1) {
    try {
        const response = await fetch('/orders/add-to-cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                product_id: parseInt(productId),
                quantity: parseInt(quantity)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Товар добавлен в корзину', 'success');
            updateCartCounter();
            
            // Анимация кнопки
            const button = document.querySelector(`[data-product-id="${productId}"]`);
            if (button) {
                animateButton(button);
            }
        } else {
            showNotification(data.message || 'Ошибка при добавлении товара', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Произошла ошибка', 'error');
    }
}

async function removeFromCart(itemId) {
    try {
        const response = await fetch('/orders/remove-from-cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                item_id: itemId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Товар удален из корзины', 'info');
            updateCartCounter();
            
            // Удаляем элемент из DOM
            const item = document.querySelector(`[data-item-id="${itemId}"]`);
            if (item) {
                item.remove();
            }
        } else {
            showNotification(data.message || 'Ошибка при удалении товара', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Произошла ошибка', 'error');
    }
}

async function updateCartCounter() {
    try {
        const response = await fetch('/orders/cart-count/');
        const data = await response.json();
        
        const counters = document.querySelectorAll('.cart-counter, .badge');
        counters.forEach(counter => {
            if (counter.closest('[href*="cart"]')) {
                counter.textContent = data.count || 0;
                
                if (data.count > 0) {
                    counter.style.display = 'inline-block';
                } else {
                    counter.style.display = 'none';
                }
            }
        });
    } catch (error) {
        console.error('Ошибка обновления счетчика корзины:', error);
    }
}

// === МОБИЛЬНОЕ МЕНЮ ===
function initMobileMenu() {
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
        
        // Закрытие при клике вне меню
        document.addEventListener('click', function(e) {
            if (!mobileMenu.contains(e.target) && !menuToggle.contains(e.target)) {
                mobileMenu.classList.remove('active');
                menuToggle.classList.remove('active');
            }
        });
    }
}

// === ЭФФЕКТЫ ПРОКРУТКИ ===
function initScrollEffects() {
    // Фиксированная шапка
    const header = document.querySelector('.header');
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (header) {
            if (scrollTop > 100) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
            
            // Скрытие/показ при прокрутке
            if (scrollTop > lastScrollTop && scrollTop > 200) {
                header.style.transform = 'translateY(-100%)';
            } else {
                header.style.transform = 'translateY(0)';
            }
        }
        
        lastScrollTop = scrollTop;
    });
    
    // Кнопка "Наверх"
    const backToTop = createBackToTopButton();
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTop.style.display = 'block';
        } else {
            backToTop.style.display = 'none';
        }
    });
}

function createBackToTopButton() {
    const button = document.createElement('button');
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.className = 'back-to-top';
    button.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #cb413b 0%, #a73530 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 20px rgba(203, 65, 59, 0.3);
        cursor: pointer;
        display: none;
        z-index: 1000;
        transition: all 0.3s ease;
    `;
    
    button.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    button.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.1)';
    });
    
    button.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
    });
    
    document.body.appendChild(button);
    return button;
}

// === ПОДСКАЗКИ ===
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const title = this.getAttribute('title') || this.getAttribute('data-title');
            if (title) {
                showTooltip(this, title);
            }
        });
        
        element.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

// === ЛЕНИВАЯ ЗАГРУЗКА ===
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// === УТИЛИТЫ ===
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 90px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        z-index: 9999;
        min-width: 300px;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    
    notification.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <span>${message}</span>
            <button class="btn-close btn-close-white ms-3" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Анимация появления
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Автоматическое удаление
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }, duration);
}

function animateButton(button) {
    const originalTransform = button.style.transform;
    button.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
        button.style.transform = 'scale(1.05)';
        setTimeout(() => {
            button.style.transform = originalTransform;
        }, 150);
    }, 150);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// === ЭКСПОРТ ФУНКЦИЙ ===
window.ZLinApp = {
    addToCart,
    removeFromCart,
    updateCartCounter,
    showNotification,
    performSearch,
    hideSearchDropdown
};