// theme.js

// Event listener for theme toggle button
document.getElementById('theme-toggle').addEventListener('click', function() {
    // Get current theme from data attribute
    const currentTheme = document.documentElement.getAttribute('data-theme');
    console.log('Current theme:', currentTheme);

    // Toggle theme
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    console.log('New theme:', newTheme);

    // Apply new theme
    document.documentElement.setAttribute('data-theme', newTheme);
    
    // Update class for body based on new theme
    if (newTheme === 'dark') {
        document.body.classList.add('dark-theme');
        console.log('Applied dark theme');
    } else {
        document.body.classList.remove('dark-theme');
        console.log('Applied light theme');
    }

    // Save preference to localStorage
    localStorage.setItem('theme', newTheme);
});

// Ensure the theme is set correctly on load
document.addEventListener('DOMContentLoaded', () => {
    const theme = localStorage.getItem('theme') || 'light';
    console.log('Loaded theme from storage:', theme);

    document.documentElement.setAttribute('data-theme', theme);
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
    }
});
