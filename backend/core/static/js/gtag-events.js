// Prestige Cars 24 - Google Ads Conversion Tracking

document.addEventListener('DOMContentLoaded', function() {
    
    // Универсальный обработчик для всех data-gtag-event
    document.querySelectorAll('[data-gtag-event]').forEach(function(el) {
        el.addEventListener('click', function() {
            const eventName = this.dataset.gtagEvent;
            const carName = this.dataset.gtagCar || '';
            const category = this.dataset.gtagCategory || '';
            
            // Базовое событие
            gtag('event', eventName, {
                'event_category': getEventCategory(eventName),
                'event_label': carName || category || eventName,
                'car_name': carName,
                'car_category': category
            });
            
            // Конверсии для важных действий
            if (eventName.includes('whatsapp') || eventName === 'hero_form_submit') {
                gtag('event', 'conversion', {
                    'send_to': 'AW-17794321096', // Заменить на реальный ID
                    'value': 1.0,
                    'currency': 'EUR'
                });
            }
        });
    });
    
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
    
    // Определение категории по имени события
    function getEventCategory(eventName) {
        if (eventName.includes('whatsapp')) return 'whatsapp';
        if (eventName.includes('phone')) return 'phone';
        if (eventName.includes('email')) return 'email';
        if (eventName.includes('book_now')) return 'booking';
        if (eventName.includes('form')) return 'form';
        return 'engagement';
    }
});