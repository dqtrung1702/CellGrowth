// CSRF helper: read cookie and attach to AJAX + POST forms
function getCookie(name) {
  const value = (`; ${document.cookie}`).split(`; ${name}=`).pop();
  return value ? value.split(';')[0] : '';
}

document.addEventListener('DOMContentLoaded', () => {
  const token = getCookie('csrf_token');
  if (!token) return;
  if (window.jQuery) {
    $.ajaxSetup({
      beforeSend: function (xhr) {
        xhr.setRequestHeader('X-CSRFToken', token);
      }
    });
  }
  document.querySelectorAll('form[method="POST"]').forEach(form => {
    if (!form.querySelector('input[name="_csrf"]')) {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = '_csrf';
      input.value = token;
      form.appendChild(input);
    }
  });
});
