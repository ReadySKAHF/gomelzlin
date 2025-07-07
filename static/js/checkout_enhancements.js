class CheckoutManager {
    constructor() {
        this.deliveryAddresses = {};
        this.baseCartTotal = parseFloat(document.getElementById('cart_subtotal')?.textContent || '0');
        
        document.addEventListener('DOMContentLoaded', () => {
            this.init();
        });
    }

    init() {
        console.log('Инициализация CheckoutManager...');
        
        this.loadSavedAddresses();
        
        this.initEventListeners();
        
        this.initFormState();
        
        console.log('CheckoutManager инициализирован');
    }

    initEventListeners() {
        const deliveryMethodSelect = document.getElementById('delivery_method');
        if (deliveryMethodSelect) {
            deliveryMethodSelect.addEventListener('change', () => this.handleDeliveryMethodChange());
        }

        const savedAddressSelect = document.getElementById('saved_address_id');
        if (savedAddressSelect) {
            savedAddressSelect.addEventListener('change', () => this.handleAddressChange());
        }

        const checkoutForm = document.getElementById('checkoutForm');
        if (checkoutForm) {
            checkoutForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        this.initAutoSave();

        this.initCompanyFieldsToggle();
    }

    initFormState() {
        this.handleDeliveryMethodChange();
        
        const savedAddressSelect = document.getElementById('saved_address_id');
        if (savedAddressSelect && savedAddressSelect.value && savedAddressSelect.value !== 'new') {
            setTimeout(() => {
                this.handleAddressChange();
            }, 100);
        }
    }

    handleDeliveryMethodChange() {
        const deliveryMethod = document.getElementById('delivery_method').value;
        const addressSection = document.getElementById('delivery_address_section');
        
        console.log('Delivery method changed to:', deliveryMethod);
        
        if (deliveryMethod === 'pickup') {
            if (addressSection) addressSection.style.display = 'none';
            this.setRequiredFields(['delivery_address'], false);
        } else {
            if (addressSection) addressSection.style.display = 'block';
            this.setRequiredFields(['delivery_address'], true);
        }
        
        this.updateDeliveryCost();
        this.updateTotalCost();
        this.showDeliveryEstimate();
    }

    async handleAddressChange() {
        const savedAddressSelect = document.getElementById('saved_address_id');
        const newAddressInput = document.getElementById('new_address_input');
        const deliveryAddressTextarea = document.getElementById('delivery_address');
        
        if (!savedAddressSelect) {
            console.log('Селект адресов не найден');
            return;
        }
        
        const savedAddressId = savedAddressSelect.value;
        console.log('Выбран адрес:', savedAddressId);
        
        if (savedAddressId === 'new') {
            if (newAddressInput) {
                newAddressInput.style.display = 'block';
            }
            if (deliveryAddressTextarea) {
                deliveryAddressTextarea.required = true;
                deliveryAddressTextarea.value = '';
                deliveryAddressTextarea.focus();
            }
            this.hideAddressPreview();
            
        } else if (savedAddressId) {
            if (newAddressInput) {
                newAddressInput.style.display = 'none';
            }
            if (deliveryAddressTextarea) {
                deliveryAddressTextarea.required = false;
            }
            
            console.log('Загружаем информацию об адресе:', savedAddressId);
            const fullAddressInfo = await this.loadFullAddressInfo(savedAddressId);
            
            if (fullAddressInfo) {
                console.log('Полная информация загружена:', fullAddressInfo);
                if (deliveryAddressTextarea) {
                    deliveryAddressTextarea.value = fullAddressInfo.full_address;
                }
                this.showAddressPreview(fullAddressInfo);
            } else {
                console.log('Используем базовую информацию из селекта');
                const selectedAddress = this.deliveryAddresses[savedAddressId];
                if (selectedAddress) {
                    console.log('Базовая информация:', selectedAddress);
                    if (deliveryAddressTextarea) {
                        deliveryAddressTextarea.value = selectedAddress.full_address;
                    }
                    this.showAddressPreview(selectedAddress);
                }
            }
        } else {
            this.hideAddressPreview();
        }
    }

    loadSavedAddresses() {
        const addressOptions = document.querySelectorAll('#saved_address_id option[value]:not([value="new"])');
        
        console.log('Найдено опций адресов:', addressOptions.length);
        
        addressOptions.forEach(option => {
            const addressId = option.value;
            if (addressId && addressId !== 'new') {
                const text = option.textContent.trim();
                const parts = text.split(' - ');
                
                if (parts.length >= 2) {
                    const title = parts[0];
                    const address = parts.slice(1).join(' - ');
                    
                    this.deliveryAddresses[addressId] = {
                        id: addressId,
                        title: title,
                        full_address: address,
                        address: address,
                        city: address.split(',')[0] || '',
                    };
                    
                    console.log(`Загружен адрес ${addressId}:`, this.deliveryAddresses[addressId]);
                }
            }
        });
        
        console.log('Все загруженные адреса:', this.deliveryAddresses);
    }

    async loadFullAddressInfo(addressId) {
        try {
            console.log('Отправляем запрос для адреса:', addressId);
            const response = await fetch(`/accounts/delivery-address/${addressId}/info/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            console.log('Ответ от сервера:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('Данные от сервера:', data);
                if (data.success) {
                    return data.address;
                }
            }
            
            return null;
        } catch (error) {
            console.error('Ошибка загрузки информации об адресе:', error);
            return null;
        }
    }

    showAddressPreview(address) {
        console.log('Показываем превью для адреса:', address);
        
        const existingPreview = document.getElementById('address_preview');
        if (existingPreview) {
            existingPreview.remove();
        }
        
        const previewElement = document.createElement('div');
        previewElement.id = 'address_preview';
        previewElement.style.cssText = `
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border: 2px solid #cb413b;
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 1rem;
            font-size: 0.95rem;
            color: #333;
            box-shadow: 0 4px 15px rgba(203, 65, 59, 0.1);
            position: relative;
            overflow: hidden;
        `;
        
        previewElement.innerHTML = `
            <div style="position: absolute; top: -10px; right: -10px; width: 40px; height: 40px; background: #cb413b; border-radius: 50%; opacity: 0.1;"></div>
            
            <div style="display: flex; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid #dee2e6; padding-bottom: 0.75rem;">
                <div style="background: #cb413b; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-size: 1.2rem;">
                    📍
                </div>
                <div>
                    <h4 style="margin: 0; color: #cb413b; font-size: 1.2rem; font-weight: 600;">${address.title}</h4>
                    <p style="margin: 0; color: #666; font-size: 0.9rem;">Выбранный адрес доставки</p>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="color: #cb413b; margin-right: 0.5rem; font-size: 1rem;">🏢</span>
                        <strong style="color: #333;">Адрес:</strong>
                    </div>
                    <p style="margin: 0 0 0 1.5rem; line-height: 1.5; color: #555;">
                        ${address.full_address || address.address || `${address.city}, ${address.address}`}
                    </p>
                    ${address.postal_code ? `
                        <p style="margin: 0.25rem 0 0 1.5rem; color: #666; font-size: 0.9rem;">
                            📮 Индекс: ${address.postal_code}
                        </p>
                    ` : ''}
                </div>
                
                <div>
                    ${address.contact_person ? `
                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                            <span style="color: #cb413b; margin-right: 0.5rem; font-size: 1rem;">👤</span>
                            <strong style="color: #333;">Контактное лицо:</strong>
                        </div>
                        <p style="margin: 0 0 0.5rem 1.5rem; color: #555;">${address.contact_person}</p>
                    ` : ''}
                    
                    ${address.contact_phone ? `
                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                            <span style="color: #cb413b; margin-right: 0.5rem; font-size: 1rem;">📞</span>
                            <strong style="color: #333;">Телефон:</strong>
                        </div>
                        <p style="margin: 0 0 0 1.5rem; color: #555;">
                            <a href="tel:${address.contact_phone}" style="color: #cb413b; text-decoration: none;">
                                ${address.contact_phone}
                            </a>
                        </p>
                    ` : ''}
                </div>
            </div>
            
            ${address.notes ? `
                <div style="background: rgba(203, 65, 59, 0.05); border-left: 4px solid #cb413b; padding: 0.75rem; border-radius: 0 8px 8px 0; margin-top: 1rem;">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="color: #cb413b; margin-right: 0.5rem; font-size: 1rem;">📝</span>
                        <strong style="color: #333;">Примечания:</strong>
                    </div>
                    <p style="margin: 0; color: #555; font-style: italic; line-height: 1.4;">
                        ${address.notes}
                    </p>
                </div>
            ` : ''}
            
            <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid #dee2e6; text-align: center;">
                <small style="color: #666;">
                    ✅ Этот адрес будет использован для доставки вашего заказа
                </small>
            </div>
        `;
        
        const savedAddressSelect = document.getElementById('saved_address_id');
        if (savedAddressSelect && savedAddressSelect.parentNode) {
            savedAddressSelect.parentNode.appendChild(previewElement);
            
            previewElement.style.opacity = '0';
            previewElement.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                previewElement.style.transition = 'all 0.3s ease';
                previewElement.style.opacity = '1';
                previewElement.style.transform = 'translateY(0)';
            }, 50);
            
            console.log('Превью добавлено на страницу');
        } else {
            console.error('Не удалось найти место для добавления превью');
        }
    }

    hideAddressPreview() {
        const previewElement = document.getElementById('address_preview');
        if (previewElement) {
            previewElement.remove();
            console.log('Превью скрыто');
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    updateDeliveryCost() {
        const deliveryMethod = document.getElementById('delivery_method')?.value;
        const deliveryCostElement = document.getElementById('delivery_cost');
        let deliveryCost = 0;
        
        if (!deliveryMethod || !deliveryCostElement) return 0;
        
        switch (deliveryMethod) {
            case 'pickup':
                deliveryCost = 0;
                deliveryCostElement.textContent = '0.00 BYN';
                break;
            case 'delivery':
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
        
        window.deliveryCost = deliveryCost;
        return deliveryCost;
    }

    updateTotalCost() {
        const deliveryCost = this.updateDeliveryCost();
        const totalCostElement = document.getElementById('total_cost');
        const deliveryMethod = document.getElementById('delivery_method')?.value;
        
        if (!totalCostElement || !deliveryMethod) return;
        
        if (deliveryMethod === 'transport_company') {
            totalCostElement.textContent = `${this.baseCartTotal.toFixed(2)} BYN + доставка`;
        } else {
            const totalCost = this.baseCartTotal + deliveryCost;
            totalCostElement.textContent = `${totalCost.toFixed(2)} BYN`;
        }
    }

    showDeliveryEstimate() {
        const deliveryMethod = document.getElementById('delivery_method')?.value;
        if (!deliveryMethod) return;
        
        const estimates = {
            'pickup': 'Готов к самовывозу в течение 1-2 рабочих дней',
            'delivery': 'Доставка в течение 1-3 рабочих дней',
            'transport_company': 'Доставка транспортной компанией в течение 3-7 рабочих дней'
        };
        
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
            if (deliveryMethodSelect && deliveryMethodSelect.parentNode) {
                deliveryMethodSelect.parentNode.appendChild(estimateElement);
            }
        }
        
        estimateElement.innerHTML = `⏰ ${estimates[deliveryMethod] || 'Срок доставки уточняется'}`;
    }

    setRequiredFields(fieldNames, required) {
        fieldNames.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (field) {
                field.required = required;
                
                const label = field.parentNode?.querySelector('label');
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
        const errors = this.validateForm();
        
        if (errors.length > 0) {
            e.preventDefault();
            this.showValidationErrors(errors);
            return false;
        }
        
        this.showLoadingState();
        
        this.trackOrderSubmission();
        
        return true;
    }

    validateForm() {
        const errors = [];
        const deliveryMethod = document.getElementById('delivery_method').value;
        
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
        
        const email = document.getElementById('customer_email').value.trim();
        if (email && !this.isValidEmail(email)) {
            errors.push('Некорректный email адрес');
            this.highlightError(document.getElementById('customer_email'));
        }
        
        const phone = document.getElementById('customer_phone').value.trim();
        if (phone && !this.isValidPhone(phone)) {
            errors.push('Некорректный номер телефона');
            this.highlightError(document.getElementById('customer_phone'));
        }
        
        const unp = document.getElementById('company_unp')?.value.trim();
        if (unp && !this.isValidUNP(unp)) {
            errors.push('УНП должен содержать 9 цифр');
            this.highlightError(document.getElementById('company_unp'));
        }
        
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
        const existingErrors = document.querySelectorAll('.validation-error');
        existingErrors.forEach(error => error.remove());
        
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
        
        const form = document.getElementById('checkoutForm');
        form.insertBefore(errorBlock, form.firstChild);

        errorBlock.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    highlightError(element) {
        element.style.borderColor = '#dc3545';
        element.style.boxShadow = '0 0 0 3px rgba(220, 53, 69, 0.1)';
        
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
        const fieldsToSave = ['customer_name', 'customer_phone', 'notes'];
        
        fieldsToSave.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                const savedValue = localStorage.getItem(`checkout_${fieldId}`);
                if (savedValue && !field.value.trim()) {
                    field.value = savedValue;
                }
                
                field.addEventListener('input', () => {
                    localStorage.setItem(`checkout_${fieldId}`, field.value);
                });
            }
        });
        
        window.addEventListener('beforeunload', () => {
            if (document.querySelector('.validation-error') === null) {
                fieldsToSave.forEach(fieldId => {
                    localStorage.removeItem(`checkout_${fieldId}`);
                });
            }
        });
    }

    initCompanyFieldsToggle() {
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
            toggleCompanyFields(); 
        }
    }

    trackOrderSubmission() {
        const analyticsData = {
            event: 'order_submission_started',
            delivery_method: document.getElementById('delivery_method').value,
            payment_method: document.getElementById('payment_method').value,
            cart_total: this.baseCartTotal,
            timestamp: new Date().toISOString()
        };
        
        console.log('Order analytics:', analyticsData);
    }

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

window.toggleDeliveryAddress = function() {
    if (window.checkoutManager) {
        window.checkoutManager.handleDeliveryMethodChange();
    }
};

window.toggleAddressInput = function() {
    if (window.checkoutManager) {
        window.checkoutManager.handleAddressChange();
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
        setTimeout(() => {
            window.checkoutManager = new CheckoutManager();
            console.log('CheckoutManager initialized successfully');
        }, 100);
    }
});
