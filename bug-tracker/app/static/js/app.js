document.addEventListener('DOMContentLoaded', function() {
    console.log('Bug Tracker App Loaded');
});

function confirmDelete(message = 'Are you sure?') {
    return confirm(message);
}
