// Prestige Cars 24 - Google Ads Conversion Tracking

document.addEventListener('DOMContentLoaded', function() {
    
    // Конфигурация конверсий
    const CONVERSIONS = {
        whatsapp: { label: 'AW-17794321096/1G3dCMvDmesbEMiV_6RC', value: 2.0 },
        phone:    { label: 'AW-17794321096/9k1-CPjzmusbEMiV_6RC', value: 2.0 },
        form:     { label: 'AW-17794321096/Rbl2CMzfmusbEMiV_6RC', value: 5.0 }
    };
    
    // Универсальный обработчик для всех data-gtag-event
    document.querySelectorAll('[data-gtag-event]').forEach(function(el) {
        el.addEventListener('click', function() {
            const eventName = this.dataset.gtagEvent;
            const carName = this.dataset.gtagCar || '';
            const category = this.dataset.gtagCategory || '';
            
            // Базовое событие GA4
            gtag('event', eventName, {
                'event_category': getEventCategory(eventName),
                'event_label': carName || category || eventName,
                'car_name': carName,
                'car_category': category
            });
            
            // Google Ads конверсии
            if (eventName.includes('whatsapp')) {
                sendConversion('whatsapp');
            } else if (eventName.includes('phone')) {
                sendConversion('phone');
            }
        });
    });
    
    // Функция отправки конверсии
    function sendConversion(type) {
        if (CONVERSIONS[type] && typeof gtag !== 'undefined') {
            gtag('event', 'conversion', {
                'send_to': CONVERSIONS[type].label,
                'value': CONVERSIONS[type].value,
                'currency': 'EUR'
            });
        }
    }
    
    // Экспорт для вызова из формы
    window.sendFormConversion = function() {
        sendConversion('form');
    };
    
    // Car Detail Page View
    const carDetailPage = document.querySelector('.car-detail-page');
    if (carDetailPage) {
        const carName = document.querySelector('.properties-title h4');
        if (carName) {
            gtag('event', 'view_item', {
                'event_category': 'car_detail',
                'event_label': carName.textContent.trim()
            });
        }
    }
    
    function getEventCategory(eventName) {
        if (eventName.includes('whatsapp')) return 'whatsapp';
        if (eventName.includes('phone')) return 'phone';
        if (eventName.includes('email')) return 'email';
        if (eventName.includes('book_now')) return 'booking';
        if (eventName.includes('form')) return 'form';
        return 'engagement';
    }
});