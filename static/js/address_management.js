// Функции для управления адресами доставки
class AddressManager {
    constructor() {
        this.modal = document.getElementById('addressModal');
        this.form = document.getElementById('addressForm');
        this.initEventListeners();
    }

    initEventListeners() {
        // Обработчик формы добавления/редактирования адреса
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // Закрытие модального окна при клике вне его
        if (this.modal) {
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) {
                    this.closeModal();
                }
            });
        }

        // Обработчики клавиатуры
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal && this.modal.style.display === 'flex') {
                this.closeModal();
            }
        });
    }

    showAddForm() {
        document.getElementById('addressModalTitle').textContent = 'Добавить адрес доставки';
        document.getElementById('addressSubmitText').textContent = '💾 Сохранить адрес';
        this.form.reset();
        document.getElementById('addressId').value = '';
        this.showModal();
    }

    showEditForm(addressId, addressData = null) {
        document.getElementById('addressModalTitle').textContent = 'Редактировать адрес';
        document.getElementById('addressSubmitText').textContent = '💾 Обновить адрес';
        document.getElementById('addressId').value = addressId;
        
        if (addressData) {
            this.fillForm(addressData);
        } else {
            // Если данные не переданы, загружаем их с сервера
            this.loadAddressData(addressId);
        }
        
        this.showModal();
    }

    fillForm(data) {
        document.getElementById('addressTitle').value = data.title || '';
        document.getElementById('addressCity').value = data.city || '';
        document.getElementById('addressFull').value = data.address || '';
        document.getElementById('addressPostal').value = data.postal_code || '';
        document.getElementById('addressContact').value = data.contact_person || '';
        document.getElementById('addressPhone').value = data.contact_phone || '';
        document.getElementById('addressNotes').value = data.notes || '';
        document.getElementById('addressDefault').checked = data.is_default || false;
    }

    showModal() {
        this.modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        // Фокусируемся на первом поле
        document.getElementById('addressTitle').focus();
    }

    closeModal() {
        this.modal.style.display = 'none';
        document.body.style.overflow = '';
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(this.form);
        const addressId = formData.get('address_id');
        
        const url = addressId ? 
            `/accounts/address/${addressId}/update/` : 
            '/accounts/address/add/';

        try {
            // Показываем индикатор загрузки
            const submitBtn = this.form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '⏳ Сохранение...';
            submitBtn.disabled = true;

            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                this.closeModal();
                
                // Обновляем страницу или добавляем адрес в список
                if (window.location.pathname.includes('profile')) {
                    location.reload();
                } else {
                    // Если мы на странице оформления заказа, обновляем селект адресов
                    this.updateAddressSelect(data.address);
                }
            } else {
                this.showNotification(data.message, 'error');
            }

            // Возвращаем кнопку в исходное состояние
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;

        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Произошла ошибка при сохранении адреса', 'error');
            
            // Возвращаем кнопку в исходное состояние
            const submitBtn = this.form.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
        }
    }

    async setDefaultAddress(addressId) {
        if (!confirm('Сделать этот адрес основным?')) {
            return;
        }

        try {
            const response = await fetch(`/accounts/address/${addressId}/set-default/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                location.reload();
            } else {
                this.showNotification(data.message, 'error');
            }

        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Произошла ошибка при установке адреса по умолчанию', 'error');
        }
    }

    async deleteAddress(addressId) {
        if (!confirm('Удалить этот адрес? Это действие нельзя будет отменить.')) {
            return;
        }

        try {
            const response = await fetch(`/accounts/address/${addressId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                
                // Удаляем карточку адреса из DOM
                const addressCard = document.querySelector(`[data-address-id="${addressId}"]`);
                if (addressCard) {
                    addressCard.remove();
                }

                // Если адресов не осталось, показываем заглушку
                if (!document.querySelectorAll('.address-card').length) {
                    location.reload();
                }
            } else {
                this.showNotification(data.message, 'error');
            }

        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Произошла ошибка при удалении адреса', 'error');
        }
    }

    updateAddressSelect(address) {
        const select = document.getElementById('saved_address_id');
        if (select) {
            // Добавляем новый адрес в селект (если это новый адрес)
            if (!document.querySelector(`option[value="${address.id}"]`)) {
                const option = document.createElement('option');
                option.value = address.id;
                option.textContent = `${address.title} - ${address.full_address}`;
                
                // Вставляем перед опцией "Ввести новый адрес"
                const newOption = select.querySelector('option[value="new"]');
                select.insertBefore(option, newOption);
            }
            
            // Выбираем новый адрес
            select.value = address.id;
            
            // Скрываем поле ввода нового адреса
            const newAddressInput = document.getElementById('new_address_input');
            if (newAddressInput) {
                newAddressInput.style.display = 'none';
            }
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    showNotification(message, type = 'info') {
        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getNotificationIcon(type)}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
            </div>
        `;

        // Добавляем стили, если их еще нет
        if (!document.getElementById('notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    max-width: 400px;
                    z-index: 10000;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    animation: slideInRight 0.3s ease-out;
                }
                
                .notification-content {
                    display: flex;
                    align-items: center;
                    padding: 1rem;
                    background: white;
                    border-radius: 8px;
                    border-left: 4px solid;
                }
                
                .notification-success .notification-content {
                    border-left-color: #28a745;
                }
                
                .notification-error .notification-content {
                    border-left-color: #dc3545;
                }
                
                .notification-info .notification-content {
                    border-left-color: #17a2b8;
                }
                
                .notification-warning .notification-content {
                    border-left-color: #ffc107;
                }
                
                .notification-icon {
                    margin-right: 0.75rem;
                    font-size: 1.2rem;
                }
                
                .notification-message {
                    flex: 1;
                    font-weight: 500;
                }
                
                .notification-close {
                    background: none;
                    border: none;
                    font-size: 1.5rem;
                    cursor: pointer;
                    color: #6c757d;
                    margin-left: 0.75rem;
                }
                
                .notification-close:hover {
                    color: #495057;
                }
                
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
            `;
            document.head.appendChild(styles);
        }

        // Добавляем уведомление в DOM
        document.body.appendChild(notification);

        // Автоматически удаляем через 5 секунд
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    async loadAddressData(addressId) {
        // Этот метод можно расширить для загрузки данных адреса с сервера
        // Пока что просто показываем форму
        console.log('Loading address data for ID:', addressId);
    }
}

// Инициализируем менеджер адресов при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    window.addressManager = new AddressManager();
});

// Глобальные функции для совместимости с существующим кодом
function showAddAddressForm() {
    if (window.addressManager) {
        window.addressManager.showAddForm();
    }
}

function closeAddressModal() {
    if (window.addressManager) {
        window.addressManager.closeModal();
    }
}

function editAddress(addressId, addressData = null) {
    if (window.addressManager) {
        window.addressManager.showEditForm(addressId, addressData);
    }
}

function setDefaultAddress(addressId) {
    if (window.addressManager) {
        window.addressManager.setDefaultAddress(addressId);
    }
}

function deleteAddress(addressId) {
    if (window.addressManager) {
        window.addressManager.deleteAddress(addressId);
    }
}