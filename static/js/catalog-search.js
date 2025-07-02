class CatalogSearch {
    constructor() {
        this.searchInput = document.getElementById('searchInput');
        this.suggestionsContainer = document.getElementById('suggestions');
        this.searchForm = document.querySelector('.search-form');
        
        this.searchTimeout = null;
        this.isSearching = false;
        this.currentQuery = '';
        this.selectedIndex = -1;
        
        this.init();
    }
    
    /**
     * Инициализация поиска
     */
    init() {
        if (!this.searchInput) return;
        
        // Привязываем события
        this.searchInput.addEventListener('input', this.handleInput.bind(this));
        this.searchInput.addEventListener('keydown', this.handleKeydown.bind(this));
        this.searchInput.addEventListener('focus', this.handleFocus.bind(this));
        this.searchInput.addEventListener('blur', this.handleBlur.bind(this));
        
        if (this.searchForm) {
            this.searchForm.addEventListener('submit', this.handleSubmit.bind(this));
        }
        
        // Скрываем предложения при клике вне поиска
        document.addEventListener('click', this.handleOutsideClick.bind(this));
        
        console.log('Catalog Search initialized');
    }
    
    /**
     * Обработка ввода в поисковой строке
     */
    handleInput(event) {
        const query = event.target.value.trim();
        this.currentQuery = query;
        this.selectedIndex = -1;
        
        // Очищаем предыдущий таймаут
        clearTimeout(this.searchTimeout);
        
        if (query.length < 2) {
            this.hideSuggestions();
            return;
        }
        
        // Устанавливаем новый таймаут для запроса
        this.searchTimeout = setTimeout(() => {
            this.fetchSuggestions(query);
        }, 300);
    }
    
    /**
     * Обработка нажатий клавиш
     */
    handleKeydown(event) {
        const suggestions = this.suggestionsContainer.querySelectorAll('.suggestion-item');
        
        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, suggestions.length - 1);
                this.updateSelection(suggestions);
                break;
                
            case 'ArrowUp':
                event.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection(suggestions);
                break;
                
            case 'Enter':
                event.preventDefault();
                if (this.selectedIndex >= 0 && suggestions[this.selectedIndex]) {
                    this.selectSuggestion(suggestions[this.selectedIndex]);
                } else {
                    this.submitSearch();
                }
                break;
                
            case 'Escape':
                this.hideSuggestions();
                this.searchInput.blur();
                break;
        }
    }
    
    /**
     * Обновление выделения в списке предложений
     */
    updateSelection(suggestions) {
        suggestions.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('selected');
            }
        });
    }
    
    /**
     * Обработка фокуса на поисковой строке
     */
    handleFocus(event) {
        if (this.currentQuery.length >= 2 && this.suggestionsContainer.children.length > 0) {
            this.showSuggestions();
        }
    }
    
    /**
     * Обработка потери фокуса
     */
    handleBlur(event) {
        // Небольшая задержка, чтобы успеть обработать клик по предложению
        setTimeout(() => {
            if (!this.suggestionsContainer.contains(document.activeElement)) {
                this.hideSuggestions();
            }
        }, 150);
    }
    
    /**
     * Обработка клика вне поисковой области
     */
    handleOutsideClick(event) {
        const searchSection = event.target.closest('.search-section');
        if (!searchSection) {
            this.hideSuggestions();
        }
    }
    
    /**
     * Обработка отправки формы
     */
    handleSubmit(event) {
        event.preventDefault();
        this.submitSearch();
    }
    
    /**
     * Отправка поискового запроса
     */
    submitSearch() {
        const query = this.searchInput.value.trim();
        
        if (query.length < 2) {
            this.showNotification('Введите минимум 2 символа для поиска', 'warning');
            return;
        }
        
        // Переход на страницу поиска
        window.location.href = `/catalog/search/?q=${encodeURIComponent(query)}`;
    }
    
    /**
     * Получение предложений с сервера
     */
    async fetchSuggestions(query) {
        if (this.isSearching) return;
        
        this.isSearching = true;
        this.showLoading();
        
        try {
            const response = await fetch(`/catalog/ajax/quick-search/?q=${encodeURIComponent(query)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.displaySuggestions(data.results || []);
            
        } catch (error) {
            console.error('Ошибка поиска:', error);
            this.showError('Ошибка при выполнении поиска');
        } finally {
            this.isSearching = false;
        }
    }
    
    /**
     * Показ индикатора загрузки
     */
    showLoading() {
        this.suggestionsContainer.innerHTML = `
            <div class="search-loading">
                Поиск...
            </div>
        `;
        this.showSuggestions();
    }
    
    /**
     * Показ ошибки
     */
    showError(message) {
        this.suggestionsContainer.innerHTML = `
            <div class="search-empty">
                <div class="search-empty-icon">⚠️</div>
                <div>${message}</div>
            </div>
        `;
        this.showSuggestions();
    }
    
    /**
     * Отображение предложений
     */
    displaySuggestions(results) {
        if (results.length === 0) {
            this.showEmptyState();
            return;
        }
        
        let html = '';
        
        results.forEach(item => {
            const emoji = this.getItemEmoji(item.name, item.category_name, item.type);
            const itemType = item.type === 'product' ? 'Товар' : 'Категория';
            
            html += `
                <div class="suggestion-item" 
                     data-url="${item.url}"
                     tabindex="0"
                     role="option">
                    
                    <div class="suggestion-emoji">
                        ${emoji}
                    </div>
                    
                    <div class="suggestion-content">
                        <div class="suggestion-title" title="${this.escapeHtml(item.name)}">
                            ${this.highlightQuery(item.name, this.currentQuery)}
                        </div>
                        
                        <div class="suggestion-meta">
                            <span class="suggestion-category">${itemType}</span>
                            
                            ${item.article ? `<span>Арт: ${item.article}</span>` : ''}
                            ${item.category_name ? `<span>• ${item.category_name}</span>` : ''}
                            ${item.product_count !== undefined ? `<span>• ${item.product_count} товаров</span>` : ''}
                        </div>
                    </div>
                </div>
            `;
        });
        
        this.suggestionsContainer.innerHTML = html;
        
        // Привязываем события к новым элементам
        this.bindSuggestionEvents();
        this.showSuggestions();
    }
    
    /**
     * Показ пустого состояния
     */
    showEmptyState() {
        this.suggestionsContainer.innerHTML = `
            <div class="search-empty">
                <div class="search-empty-icon">🔍</div>
                <div>Ничего не найдено</div>
                <div style="font-size: 0.8rem; margin-top: 0.5rem;">
                    Попробуйте изменить поисковый запрос
                </div>
            </div>
        `;
        this.showSuggestions();
    }
    
    /**
     * Привязка событий к предложениям
     */
    bindSuggestionEvents() {
        const suggestions = this.suggestionsContainer.querySelectorAll('.suggestion-item');
        
        suggestions.forEach(item => {
            item.addEventListener('click', () => this.selectSuggestion(item));
            item.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    this.selectSuggestion(item);
                }
            });
        });
    }
    
    /**
     * Выбор предложения
     */
    selectSuggestion(item) {
        const url = item.dataset.url;
        if (url) {
            window.location.href = url;
        }
    }
    
    /**
     * Показ предложений
     */
    showSuggestions() {
        this.suggestionsContainer.style.display = 'block';
    }
    
    /**
     * Скрытие предложений
     */
    hideSuggestions() {
        this.suggestionsContainer.style.display = 'none';
        this.selectedIndex = -1;
    }
    
    /**
     * Получение эмодзи для элемента
     */
    getItemEmoji(name, categoryName, type) {
        const lowerName = name.toLowerCase();
        const lowerCategory = (categoryName || '').toLowerCase();
        
        if (type === 'category') {
            // Эмодзи для категорий
            if (lowerName.includes('зерно')) return '🌾';
            if (lowerName.includes('кормо')) return '🚜';
            if (lowerName.includes('картофель')) return '🥔';
            if (lowerName.includes('метиз')) return '🔩';
            if (lowerName.includes('бункер')) return '📦';
            if (lowerName.includes('режущ')) return '⚔️';
            if (lowerName.includes('носилки')) return '🚚';
            if (lowerName.includes('новинки')) return '✨';
            if (lowerName.includes('прочие') || lowerName.includes('услуги')) return '🛠️';
            return '📁';
        } else {
            // Эмодзи для товаров
            if (lowerName.includes('жатка') || lowerCategory.includes('зерно')) return '🌾';
            if (lowerName.includes('комбайн') || lowerCategory.includes('кормо')) return '🚜';
            if (lowerName.includes('картофель')) return '🥔';
            if (lowerName.includes('болт') || lowerName.includes('гайка') || lowerCategory.includes('метиз')) return '🔩';
            if (lowerName.includes('бункер')) return '📦';
            if (lowerName.includes('режущ')) return '⚔️';
            if (lowerName.includes('носилки')) return '🚚';
            return '🏭';
        }
    }
    
    /**
     * Подсветка поискового запроса в тексте
     */
    highlightQuery(text, query) {
        if (!query || query.length < 2) return this.escapeHtml(text);
        
        const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
        return this.escapeHtml(text).replace(regex, '<strong style="color: #cb413b;">$1</strong>');
    }
    
    /**
     * Экранирование HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Экранирование регулярного выражения
     */
    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    /**
     * Показ уведомления
     */
    showNotification(message, type = 'info') {
        // Простая реализация уведомления
        // В будущем можно заменить на более сложную систему уведомлений
        alert(message);
    }
    
    /**
     * Поиск по популярным запросам
     */
    searchFor(query) {
        this.searchInput.value = query;
        this.currentQuery = query;
        window.location.href = `/catalog/search/?q=${encodeURIComponent(query)}`;
    }
}

/**
 * Глобальные функции для совместимости
 */
function handleSearchInput(event) {
    if (window.catalogSearch) {
        window.catalogSearch.handleInput(event);
    }
}

function handleSearch(event) {
    if (window.catalogSearch) {
        return window.catalogSearch.handleSubmit(event);
    }
    return false;
}

function searchFor(query) {
    if (window.catalogSearch) {
        window.catalogSearch.searchFor(query);
    }
}

/**
 * Инициализация при загрузке DOM
 */
document.addEventListener('DOMContentLoaded', function() {
    window.catalogSearch = new CatalogSearch();
});

/**
 * Дополнительные утилиты для работы с поиском
 */
const SearchUtils = {
    /**
     * Дебаунс функция
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Получение параметров URL
     */
    getUrlParams() {
        const params = new URLSearchParams(window.location.search);
        return Object.fromEntries(params.entries());
    },
    
    /**
     * Форматирование числа товаров
     */
    formatProductCount(count) {
        if (count === 1) return '1 товар';
        if (count >= 2 && count <= 4) return `${count} товара`;
        return `${count} товаров`;
    }
};

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CatalogSearch, SearchUtils };
}