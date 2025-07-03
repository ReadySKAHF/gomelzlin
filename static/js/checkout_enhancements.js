class CheckoutManager {
    constructor() {
        this.deliveryAddresses = {}; // Кэш адресов доставки
        // Получаем сумму корзины из глобальной переменной или Django переменной
        this.baseCartTotal = window.cartSubtotal || 0;
        
        this.initEventListeners();
        this.loadSavedAddresses();
        this.updateTotalCost();
    }

    initEventListeners() {
        // Изменение способа доставки
        const deliveryMethodSelect = document.getElementById('delivery_method');
        if (deliveryMethodSelect) {
            deliveryMethodSelect.addEventListener('change', () => this.handleDeliveryMethodChange());
        }

        // Изменение выбора адреса
        const savedAddressSelect = document.getElementById('saved_address_id');
        if (savedAddressSelect) {
            savedAddressSelect.addEventListener('change', () => this.handleAddressSelectionChange());
        }

        // Валидация формы при отправке
        const checkoutForm = document.getElementById('checkoutForm');
        if (checkoutForm) {
            checkoutForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // Автосохранение данных
        this.initAutoSave();

        // Показ дополнительных полей для организаций
        this.initCompanyFieldsToggle();
    }

    handleDeliveryMethodChange() {
        const deliveryMethod = document.getElementById('delivery_method').value;
        const addressSection = document.getElementById('delivery_address_section');
        
        console.log('Delivery method changed to:', deliveryMethod);
        
        if (deliveryMethod === 'pickup') {
            addressSection.style.display = 'none';
            this.setRequiredFields(['delivery_address'], false);
        } else {
            addressSection.style.display = 'block';
            this.setRequiredFields(['delivery_address'], true);
        }
        
        this.updateDeliveryCost();
        this.updateTotalCost();
        this.showDeliveryEstimate();
    }

    handleAddressSelectionChange() {
        const savedAddressId = document.getElementById('saved_address_id')?.value;
        const newAddressInput = document.getElementById('new_address_input');
        const deliveryAddressTextarea = document.getElementById('delivery_address');
        
        if (!savedAddressId) return;
        
        if (savedAddressId === 'new') {
            newAddressInput.style.display = 'block';
            deliveryAddressTextarea.required = true;
            deliveryAddressTextarea.value = '';
            deliveryAddressTextarea.focus();
            
            // Скрываем превью адреса
            this.hideAddressPreview();
        } else {
            newAddressInput.style.display = 'none';
            deliveryAddressTextarea.required = false;
            
            // Заполняем скрытое поле данными выбранного адреса
            const selectedAddress = this.deliveryAddresses[savedAddressId];
            if (selectedAddress) {
                deliveryAddressTextarea.value = selectedAddress.full_address;
                this.showAddressPreview(selectedAddress);
            }
        }
    }

    showAddressPreview(address) {
        // Показываем превью выбранного адреса
        let previewElement = document.getElementById('address_preview');
        if (!previewElement) {
            previewElement = document.createElement('div');
            previewElement.id = 'address_preview';
            previewElement.style.cssText = `
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 1rem;
                margin-top: 0.5rem;
                font-size: 0.9rem;
                color: #333;
            `;
            
            const savedAddressSelect = document.getElementById('saved_address_id');
            savedAddressSelect.parentNode.appendChild(previewElement);
        }
        
        previewElement.innerHTML = `
            <strong>📍 ${address.title}</strong><br>
            ${address.full_address}
            ${address.contact_person ? `<br><strong>Контакт:</strong> ${address.contact_person}` : ''}
            ${address.contact_phone ? ` (${address.contact_phone})` : ''}
            ${address.notes ? `<br><em>${address.notes}</em>` : ''}
        `;
        previewElement.style.display = 'block';
    }

    hideAddressPreview() {
        const previewElement = document.getElementById('address_preview');
        if (previewElement) {
            previewElement.style.display = 'none';
        }
    }

    updateDeliveryCost() {
        const deliveryMethod = document.getElementById('delivery_method').value;
        const deliveryCostElement = document.getElementById('delivery_cost');
        let deliveryCost = 0;
        
        switch (deliveryMethod) {
            case 'pickup':
                deliveryCost = 0;
                deliveryCostElement.textContent = '0.00 BYN';
                break;
            case 'delivery':
                // Бесплатная доставка для заказов свыше 500 BYN
                deliveryCost = this.baseCartTotal >= 500 ? 0 : 10;
                if (deliveryCost === 0) {
                    deliveryCostElement.textContent = 'Бесплатно (сумма ≥ 500 BYN)';
                } else {
                    deliveryCostElement.textContent = `${deliveryCost.toFixed(2)} BYN`;
                }
                break;
            case 'transport_company':
                deliveryCost = 0;
                deliveryCostElement.textContent = 'По согласованию';
                break;
        }
        
        // Обновляем глобальную переменную для совместимости
        window.deliveryCost = deliveryCost;
        
        return deliveryCost;
    }

    updateTotalCost() {
        const deliveryCost = this.updateDeliveryCost();
        const totalCostElement = document.getElementById('total_cost');
        const deliveryMethod = document.getElementById('delivery_method').value;
        
        if (deliveryMethod === 'transport_company') {
            totalCostElement.textContent = `${this.baseCartTotal.toFixed(2)} BYN + доставка`;
        } else {
            const totalCost = this.baseCartTotal + deliveryCost;
            totalCostElement.textContent = `${totalCost.toFixed(2)} BYN`;
        }
        
        console.log('Total cost updated to:', totalCostElement.textContent);
    }

    showDeliveryEstimate() {
        const deliveryMethod = document.getElementById('delivery_method').value;
        const estimates = {
            'pickup': 'Готов к самовывозу в течение 1-2 рабочих дней',
            'delivery': 'Доставка в течение 1-3 рабочих дней',
            'transport_company': 'Доставка транспортной компанией в течение 3-7 рабочих дней'
        };
        
        // Показываем оценку времени доставки
        let estimateElement = document.getElementById('delivery_estimate');
        if (!estimateElement) {
            estimateElement = document.createElement('div');
            estimateElement.id = 'delivery_estimate';
            estimateElement.style.cssText = `
                background: #e7f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 6px;
                padding: 0.75rem;
                margin-top: 0.5rem;
                font-size: 0.9rem;
                color: #0066cc;
            `;
            
            const deliveryMethodSelect = document.getElementById('delivery_method');
            deliveryMethodSelect.parentNode.appendChild(estimateElement);
        }
        
        estimateElement.innerHTML = `⏰ ${estimates[deliveryMethod] || 'Срок доставки уточняется'}`;
    }

    loadSavedAddresses() {
        // Загружаем данные сохраненных адресов для JavaScript
        const addressOptions = document.querySelectorAll('#saved_address_id option[value]:not([value="new"])');
        
        addressOptions.forEach(option => {
            const addressId = option.value;
            if (addressId && addressId !== 'new') {
                // Парсим данные из текста опции
                const text = option.textContent.trim();
                const parts = text.split(' - ');
                
                if (parts.length >= 2) {
                    const title = parts[0];
                    const address = parts.slice(1).join(' - '); // На случай если в адресе есть дефисы
                    
                    this.deliveryAddresses[addressId] = {
                        id: addressId,
                        title: title,
                        full_address: address,
                        // Дополнительные данные можно получить через AJAX при необходимости
                    };
                }
            }
        });
        
        console.log('Loaded delivery addresses:', this.deliveryAddresses);
    }

    setRequiredFields(fieldNames, required) {
        fieldNames.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (field) {
                field.required = required;
                
                // Добавляем визуальную индикацию
                const label = field.parentNode.querySelector('label');
                if (label) {
                    if (required && !label.textContent.includes('*')) {
                        label.textContent += ' *';
                    } else if (!required && label.textContent.includes('*')) {
                        label.textContent = label.textContent.replace(' *', '');
                    }
                }
            }
        });
    }

    handleFormSubmit(e) {
        // Дополнительная валидация перед отправкой
        const errors = this.validateForm();
        
        if (errors.length > 0) {
            e.preventDefault();
            this.showValidationErrors(errors);
            return false;
        }
        
        // Показываем индикатор загрузки
        this.showLoadingState();
        
        // Сохраняем данные для analytics
        this.trackOrderSubmission();
        
        return true;
    }

    validateForm() {
        const errors = [];
        const deliveryMethod = document.getElementById('delivery_method').value;
        
        // Проверяем обязательные поля
        const requiredFields = [
            { id: 'customer_name', name: 'ФИО' },
            { id: 'customer_email', name: 'Email' },
            { id: 'customer_phone', name: 'Телефон' }
        ];
        
        requiredFields.forEach(field => {
            const element = document.getElementById(field.id);
            if (!element.value.trim()) {
                errors.push(`Поле "${field.name}" обязательно для заполнения`);
                this.highlightError(element);
            }
        });
        
        // Проверяем email
        const email = document.getElementById('customer_email').value.trim();
        if (email && !this.isValidEmail(email)) {
            errors.push('Некорректный email адрес');
            this.highlightError(document.getElementById('customer_email'));
        }
        
        // Проверяем телефон
        const phone = document.getElementById('customer_phone').value.trim();
        if (phone && !this.isValidPhone(phone)) {
            errors.push('Некорректный номер телефона');
            this.highlightError(document.getElementById('customer_phone'));
        }
        
        // Проверяем УНП
        const unp = document.getElementById('company_unp')?.value.trim();
        if (unp && !this.isValidUNP(unp)) {
            errors.push('УНП должен содержать 9 цифр');
            this.highlightError(document.getElementById('company_unp'));
        }
        
        // Проверяем адрес доставки
        if (deliveryMethod !== 'pickup') {
            const savedAddressId = document.getElementById('saved_address_id')?.value;
            const deliveryAddress = document.getElementById('delivery_address').value.trim();
            
            if ((!savedAddressId || savedAddressId === 'new') && !deliveryAddress) {
                errors.push('Укажите адрес доставки');
                this.highlightError(document.getElementById('delivery_address'));
            }
        }
        
        return errors;
    }

    showValidationErrors(errors) {
        // Удаляем предыдущие ошибки
        const existingErrors = document.querySelectorAll('.validation-error');
        existingErrors.forEach(error => error.remove());
        
        // Создаем блок с ошибками
        const errorBlock = document.createElement('div');
        errorBlock.className = 'validation-error';
        errorBlock.style.cssText = `
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            color: #721c24;
        `;
        
        errorBlock.innerHTML = `
            <h4 style="margin: 0 0 0.5rem 0;">❌ Пожалуйста, исправьте следующие ошибки:</h4>
            <ul style="margin: 0; padding-left: 1.5rem;">
                ${errors.map(error => `<li>${error}</li>`).join('')}
            </ul>
        `;
        
        // Вставляем блок в начало формы
        const form = document.getElementById('checkoutForm');
        form.insertBefore(errorBlock, form.firstChild);
        
        // Прокручиваем к ошибкам
        errorBlock.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    highlightError(element) {
        element.style.borderColor = '#dc3545';
        element.style.boxShadow = '0 0 0 3px rgba(220, 53, 69, 0.1)';
        
        // Убираем подсветку при фокусе
        element.addEventListener('focus', function() {
            this.style.borderColor = '';
            this.style.boxShadow = '';
        }, { once: true });
    }

    showLoadingState() {
        const submitBtn = document.querySelector('#checkoutForm button[type="submit"]');
        if (submitBtn) {
            submitBtn.innerHTML = '⏳ Оформляем заказ...';
            submitBtn.disabled = true;
        }
        
        // Блокируем форму
        const form = document.getElementById('checkoutForm');
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.8);
            z-index: 999;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        `;
        overlay.innerHTML = '⏳ Обработка заказа...';
        
        form.style.position = 'relative';
        form.appendChild(overlay);
    }

    initAutoSave() {
        // Автосохранение данных формы (кроме чувствительных данных)
        const fieldsToSave = ['customer_name', 'customer_phone', 'notes'];
        
        fieldsToSave.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                // Восстанавливаем сохраненные данные только если поле пустое
                const savedValue = localStorage.getItem(`checkout_${fieldId}`);
                if (savedValue && !field.value.trim()) {
                    field.value = savedValue;
                }
                
                // Сохраняем при изменении
                field.addEventListener('input', () => {
                    localStorage.setItem(`checkout_${fieldId}`, field.value);
                });
            }
        });
        
        // Очищаем автосохранение при успешной отправке
        window.addEventListener('beforeunload', () => {
            if (document.querySelector('.validation-error') === null) {
                fieldsToSave.forEach(fieldId => {
                    localStorage.removeItem(`checkout_${fieldId}`);
                });
            }
        });
    }

    initCompanyFieldsToggle() {
        // Показ/скрытие полей организации в зависимости от заполнения
        const companyNameField = document.getElementById('company_name');
        if (companyNameField) {
            const toggleCompanyFields = () => {
                const isCompany = companyNameField.value.trim().length > 0;
                const companyFields = document.querySelectorAll('#company_unp, #company_address');
                
                companyFields.forEach(field => {
                    field.style.opacity = isCompany ? '1' : '0.5';
                    field.style.pointerEvents = isCompany ? 'auto' : 'none';
                });
            };
            
            companyNameField.addEventListener('input', toggleCompanyFields);
            toggleCompanyFields(); // Инициализация
        }
    }

    trackOrderSubmission() {
        // Отправляем данные в аналитику (если настроена)
        const analyticsData = {
            event: 'order_submission_started',
            delivery_method: document.getElementById('delivery_method').value,
            payment_method: document.getElementById('payment_method').value,
            cart_total: this.baseCartTotal,
            timestamp: new Date().toISOString()
        };
        
        // Здесь можно добавить отправку в Google Analytics, Yandex.Metrica и т.д.
        console.log('Order analytics:', analyticsData);
    }

    // Вспомогательные методы валидации
    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    isValidPhone(phone) {
        return /^\+?[\d\s\-\(\)]{7,}$/.test(phone);
    }

    isValidUNP(unp) {
        return /^\d{9}$/.test(unp);
    }
}

// Глобальные функции для совместимости со встроенным JavaScript в шаблоне
window.toggleDeliveryAddress = function() {
    if (window.checkoutManager) {
        window.checkoutManager.handleDeliveryMethodChange();
    }
};

window.toggleAddressInput = function() {
    if (window.checkoutManager) {
        window.checkoutManager.handleAddressSelectionChange();
    }
};

window.updateTotalCost = function() {
    if (window.checkoutManager) {
        window.checkoutManager.updateTotalCost();
    }
};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('checkoutForm')) {
        // Ждем, пока загрузится основной скрипт шаблона
        setTimeout(() => {
            window.checkoutManager = new CheckoutManager();
            console.log('CheckoutManager initialized successfully');
        }, 100);
    }
});