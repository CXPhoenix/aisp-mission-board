// Global Modal System for replacing alert(), prompt(), and confirm()

// Modal IDs
const MODAL_IDS = {
    ALERT: 'global-alert-modal',
    CONFIRM: 'global-confirm-modal',
    PROMPT: 'global-prompt-modal'
};

// Show alert modal
function showAlert(message, title = 'Ð:') {
    const modalElement = document.getElementById(MODAL_IDS.ALERT);
    const titleElement = modalElement.querySelector('[data-modal-title]');
    const messageElement = modalElement.querySelector('[data-modal-message]');
    
    titleElement.textContent = title;
    messageElement.textContent = message;
    
    const modal = new Modal(modalElement);
    modal.show();
}

// Show confirm modal
function showConfirm(message, title = 'º', onConfirm = null, onCancel = null) {
    const modalElement = document.getElementById(MODAL_IDS.CONFIRM);
    const titleElement = modalElement.querySelector('[data-modal-title]');
    const messageElement = modalElement.querySelector('[data-modal-message]');
    const confirmBtn = modalElement.querySelector('[data-modal-confirm]');
    const cancelBtn = modalElement.querySelector('[data-modal-cancel]');
    
    titleElement.textContent = title;
    messageElement.innerHTML = message; // Use innerHTML to support line breaks
    
    // Remove existing event listeners
    const newConfirmBtn = confirmBtn.cloneNode(true);
    const newCancelBtn = cancelBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
    
    const modal = new Modal(modalElement);
    
    // Add event listeners
    newConfirmBtn.addEventListener('click', () => {
        modal.hide();
        if (onConfirm) onConfirm();
    });
    
    newCancelBtn.addEventListener('click', () => {
        modal.hide();
        if (onCancel) onCancel();
    });
    
    modal.show();
}

// Show prompt modal
function showPrompt(message, title = '8e', defaultValue = '', isRequired = false, onConfirm = null, onCancel = null) {
    const modalElement = document.getElementById(MODAL_IDS.PROMPT);
    const titleElement = modalElement.querySelector('[data-modal-title]');
    const messageElement = modalElement.querySelector('[data-modal-message]');
    const inputElement = modalElement.querySelector('[data-modal-input]');
    const confirmBtn = modalElement.querySelector('[data-modal-confirm]');
    const cancelBtn = modalElement.querySelector('[data-modal-cancel]');
    const errorElement = modalElement.querySelector('[data-modal-error]');
    
    titleElement.textContent = title;
    messageElement.textContent = message;
    inputElement.value = defaultValue;
    errorElement.classList.add('hidden');
    
    // Remove existing event listeners
    const newConfirmBtn = confirmBtn.cloneNode(true);
    const newCancelBtn = cancelBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
    
    const modal = new Modal(modalElement);
    
    // Add event listeners
    newConfirmBtn.addEventListener('click', () => {
        const value = inputElement.value.trim();
        
        if (isRequired && value === '') {
            errorElement.textContent = 'dMºÅk';
            errorElement.classList.remove('hidden');
            return;
        }
        
        modal.hide();
        if (onConfirm) onConfirm(value);
    });
    
    newCancelBtn.addEventListener('click', () => {
        modal.hide();
        if (onCancel) onCancel();
    });
    
    // Enter key support
    inputElement.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            newConfirmBtn.click();
        }
    });
    
    modal.show();
    
    // Focus on input
    setTimeout(() => {
        inputElement.focus();
        inputElement.select();
    }, 100);
}

// Compatibility functions for easy replacement
window.showAlert = showAlert;
window.showConfirm = showConfirm;
window.showPrompt = showPrompt;