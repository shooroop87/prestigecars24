// static/js/forms.js - Обработка форм

document.addEventListener('DOMContentLoaded', function() {
    
    // === HERO BOOKING FORM ===
    const heroForm = document.querySelector('.flat-tab-form form, .flat-tab-form .form-title');
    if (heroForm) {
        const submitBtn = heroForm.querySelector('.btn-send-custom');
        if (submitBtn) {
            submitBtn.addEventListener('click', function(e) {
                e.preventDefault();
                submitBookingForm();
            });
        }
    }
    
    // === CONTACT FORM ===
    const contactForm = document.querySelector('.form-contact');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitContactForm(this);
        });
    }
    
    // === FAQ FORM ===
    const faqForm = document.querySelector('.form-faq');
    if (faqForm) {
        faqForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitContactForm(this);
        });
    }
});

function submitBookingForm() {
    const form = document.querySelector('.flat-tab-form');
    const btn = form.querySelector('.btn-send-custom');
    const originalText = btn.innerHTML;
    
    // Собираем данные
    const data = {
        pickup_location: form.querySelector('input[placeholder*="location"]')?.value || '',
        date: form.querySelector('input[type="date"]')?.value || '',
        time: form.querySelector('input[type="time"]')?.value || '',
        car_class: form.querySelector('select')?.value || '',
        dropoff_location: form.querySelector('input[placeholder*="Drop"]')?.value || '',
        phone: form.querySelector('input[type="tel"]')?.value || '',
    };
    
    // Валидация
    if (!data.phone) {
        showNotification('Please enter your phone number', 'error');
        return;
    }
    
    // Loading state
    btn.innerHTML = '<span>Sending...</span>';
    btn.disabled = true;
    
    // CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                      getCookie('csrftoken');
    
    fetch('/api/booking/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: new URLSearchParams(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.status === 'success') {
            showNotification(result.message, 'success');
            // Clear form
            form.querySelectorAll('input:not([type="hidden"])').forEach(input => {
                if (input.type !== 'date') input.value = '';
            });
            
            // Track conversion
            if (typeof gtag !== 'undefined') {
                gtag('event', 'conversion', {
                    'send_to': 'AW-17794321096', // Заменить на реальный ID
                    'value': 1.0,
                    'currency': 'EUR'
                });
            }
        } else {
            showNotification(result.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Connection error. Please try WhatsApp.', 'error');
    })
    .finally(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}

function submitContactForm(form) {
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    
    const formData = new FormData(form);
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    btn.innerHTML = '<span>Sending...</span>';
    btn.disabled = true;
    
    fetch('/api/contact/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        if (result.status === 'success') {
            showNotification(result.message, 'success');
            form.reset();
            
            // Track conversion
            if (typeof gtag !== 'undefined') {
                gtag('event', 'generate_lead', {
                    'event_category': 'Contact',
                    'event_label': 'Contact Form'
                });
            }
        } else {
            showNotification(result.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Connection error. Please try WhatsApp.', 'error');
    })
    .finally(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}

function showNotification(message, type = 'info') {
    // Удаляем старые уведомления
    document.querySelectorAll('.notification-toast').forEach(el => el.remove());
    
    const toast = document.createElement('div');
    toast.className = `notification-toast notification-${type}`;
    toast.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${type === 'success' ? '✓' : '!'}</span>
            <span class="notification-message">${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Анимация появления
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Автоскрытие
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
