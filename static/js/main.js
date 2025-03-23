// Initialize Feather icons
document.addEventListener('DOMContentLoaded', function() {
  feather.replace();
  
  // Initialize tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

// Function to copy content to clipboard
function copyToClipboard(elementId) {
  const element = document.getElementById(elementId);
  
  if (!element) {
    console.error(`Element with ID ${elementId} not found`);
    return;
  }
  
  let textToCopy = '';
  
  // Handle different element types
  if (element.tagName === 'TABLE') {
    // For tables, extract data into CSV format
    const rows = element.querySelectorAll('tr');
    rows.forEach(row => {
      const columns = row.querySelectorAll('th, td');
      const rowData = [];
      columns.forEach(column => {
        // Get text content, remove any commas to avoid CSV issues
        let cellText = column.textContent.trim().replace(/,/g, ' ');
        rowData.push(`"${cellText}"`);
      });
      textToCopy += rowData.join(',') + '\n';
    });
  } else if (element.tagName === 'UL' || element.tagName === 'OL') {
    // For lists, extract items
    const items = element.querySelectorAll('li');
    items.forEach(item => {
      textToCopy += item.textContent.trim() + '\n';
    });
  } else {
    // For other elements, just take the text content
    textToCopy = element.textContent;
  }
  
  // Create a temporary textarea to copy from
  const textarea = document.createElement('textarea');
  textarea.value = textToCopy;
  document.body.appendChild(textarea);
  textarea.select();
  
  try {
    // Execute copy command
    document.execCommand('copy');
    showToast('Content copied to clipboard!');
  } catch (err) {
    console.error('Failed to copy content: ', err);
    showToast('Failed to copy content to clipboard', 'error');
  }
  
  // Clean up
  document.body.removeChild(textarea);
}

// Function to show toast notification
function showToast(message, type = 'success') {
  // Check if toast container exists, if not create it
  let toastContainer = document.querySelector('.toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(toastContainer);
  }
  
  // Create toast element
  const toastEl = document.createElement('div');
  toastEl.className = `toast ${type === 'error' ? 'bg-danger text-white' : 'bg-success text-white'}`;
  toastEl.setAttribute('role', 'alert');
  toastEl.setAttribute('aria-live', 'assertive');
  toastEl.setAttribute('aria-atomic', 'true');
  
  // Add toast content
  toastEl.innerHTML = `
    <div class="toast-header ${type === 'error' ? 'bg-danger text-white' : 'bg-success text-white'}">
      <strong class="me-auto">${type === 'error' ? 'Error' : 'Success'}</strong>
      <button type="button" class="btn-close btn-close-white ms-2 mb-1" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body">
      ${message}
    </div>
  `;
  
  // Add to container
  toastContainer.appendChild(toastEl);
  
  // Initialize and show toast
  const toast = new bootstrap.Toast(toastEl, {
    autohide: true,
    delay: 3000
  });
  toast.show();
  
  // Remove after hiding
  toastEl.addEventListener('hidden.bs.toast', function() {
    toastContainer.removeChild(toastEl);
  });
}

// Prefill the URL field with example.com if empty
document.addEventListener('DOMContentLoaded', function() {
  const urlInput = document.getElementById('url');
  if (urlInput && !urlInput.value) {
    urlInput.placeholder = 'Enter URL (e.g., https://example.com)';
  }
});
