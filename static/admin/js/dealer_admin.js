document.addEventListener('DOMContentLoaded', function() {

    function setupAddressAutocomplete() {
        const cityField = document.querySelector('#id_city');
        const addressField = document.querySelector('#id_address');
        const latField = document.querySelector('#id_latitude');
        const lngField = document.querySelector('#id_longitude');
        
        if (cityField && addressField && latField && lngField) {
            const button = document.createElement('button');
            button.type = 'button';
            button.textContent = '📍 Получить координаты';
            button.className = 'btn btn-secondary';
            button.style.marginLeft = '10px';
            
            button.addEventListener('click', function() {
                const city = cityField.value;
                const address = addressField.value;
                
                if (city && address) {
                    alert(`Функция получения координат будет добавлена в следующих версиях.\nАдрес: ${city}, ${address}`);
                } else {
                    alert('Пожалуйста, заполните город и адрес');
                }
            });

            if (lngField.parentNode) {
                lngField.parentNode.appendChild(button);
            }
        }
    }

    function setupCoordinateValidation() {
        const latField = document.querySelector('#id_latitude');
        const lngField = document.querySelector('#id_longitude');
        
        if (latField) {
            latField.addEventListener('input', function() {
                const value = parseFloat(this.value);
                if (value < -90 || value > 90) {
                    this.style.borderColor = '#dc3545';
                    this.title = 'Широта должна быть от -90 до 90';
                } else {
                    this.style.borderColor = '#28a745';
                    this.title = 'Корректная широта';
                }
            });
        }
        
        if (lngField) {
            lngField.addEventListener('input', function() {
                const value = parseFloat(this.value);
                if (value < -180 || value > 180) {
                    this.style.borderColor = '#dc3545';
                    this.title = 'Долгота должна быть от -180 до 180';
                } else {
                    this.style.borderColor = '#28a745';
                    this.title = 'Корректная долгота';
                }
            });
        }
    }

    function setupMapPreview() {
        const latField = document.querySelector('#id_latitude');
        const lngField = document.querySelector('#id_longitude');
        const cityField = document.querySelector('#id_city');
        const addressField = document.querySelector('#id_address');
        
        function updatePreview() {
            const lat = latField?.value;
            const lng = lngField?.value;
            const city = cityField?.value;
            const address = addressField?.value;
            
            let previewDiv = document.querySelector('#map-preview');
            if (!previewDiv) {
                previewDiv = document.createElement('div');
                previewDiv.id = 'map-preview';
                previewDiv.style.cssText = `
                    margin-top: 10px;
                    padding: 10px;
                    background: #f8f9fa;
                    border-radius: 5px;
                    border-left: 4px solid #cb413b;
                `;

                const targetField = lngField || addressField;
                if (targetField && targetField.parentNode) {
                    targetField.parentNode.appendChild(previewDiv);
                }
            }
            
            if (lat && lng) {
                const mapsUrl = `https://yandex.by/maps/?pt=${lng},${lat}&z=16&l=map`;
                previewDiv.innerHTML = `
                    <strong>Предварительный просмотр:</strong><br>
                    <a href="${mapsUrl}" target="_blank" style="color: #cb413b;">
                        🗺️ Открыть на Яндекс картах (координаты)
                    </a>
                `;
            } else if (city && address) {
                const searchQuery = encodeURIComponent(`${city}, ${address}`);
                const mapsUrl = `https://yandex.by/maps/?text=${searchQuery}`;
                previewDiv.innerHTML = `
                    <strong>Предварительный просмотр:</strong><br>
                    <a href="${mapsUrl}" target="_blank" style="color: #cb413b;">
                        🗺️ Открыть на Яндекс картах (поиск по адресу)
                    </a>
                `;
            } else {
                previewDiv.innerHTML = `
                    <strong>Предварительный просмотр:</strong><br>
                    <span style="color: #6c757d;">Заполните координаты или адрес для предварительного просмотра</span>
                `;
            }
        }

        [latField, lngField, cityField, addressField].forEach(field => {
            if (field) {
                field.addEventListener('input', updatePreview);
            }
        });
        
        updatePreview();
    }

    setupAddressAutocomplete();
    setupCoordinateValidation();
    setupMapPreview();

    function improveListDisplay() {

        const nameCells = document.querySelectorAll('.field-name');
        nameCells.forEach(cell => {
            if (cell.textContent.length > 30) {
                cell.title = cell.textContent;
            }
        });

        const actionLinks = document.querySelectorAll('.related-widget-wrapper a');
        actionLinks.forEach(link => {
            if (link.textContent.includes('Изменить')) {
                link.innerHTML = '✏️ ' + link.innerHTML;
            } else if (link.textContent.includes('Удалить')) {
                link.innerHTML = '🗑️ ' + link.innerHTML;
            }
        });
    }
    
    improveListDisplay();
    
    console.log('Админка дилерских центров загружена и улучшена!');
});