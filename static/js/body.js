document.addEventListener('DOMContentLoaded', function() {
    // Menu functionality (if you have it)
    const menuIcon = document.getElementById('menuIcon');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const closeIcon = document.getElementById('closeIcon');

    // Show dropdown menu when menu icon is clicked
    menuIcon.addEventListener('click', function() {
        dropdownMenu.classList.add('show');
    });

    // Hide dropdown menu when close icon is clicked
    closeIcon.addEventListener('click', function() {
        dropdownMenu.classList.remove('show');
    });

    // Product slider functionality
    const products = document.querySelectorAll('.product');
    const prevButton = document.querySelector('.prev-button');
    const nextButton = document.querySelector('.next-button');

    let currentProductIndex = 0;
    let sliderInterval;

    function updateSlider() {
        // Hide all products
        products.forEach((product, index) => {
            product.style.display = index === currentProductIndex ? 'block' : 'none';
        });

        // Update product name and description
        const currentProduct = products[currentProductIndex];
        const name = currentProduct.querySelector('.product-name').textContent;
        const description = currentProduct.querySelector('.product-description').textContent;

        // Update the display
        document.querySelector('.displayed-product-name').textContent = name;
        document.querySelector('.displayed-product-description').textContent = description;
    }

    function startSliderInterval() {
        // Clear any existing interval
        clearInterval(sliderInterval);
        // Set a new interval to change the product every 3 seconds
        sliderInterval = setInterval(() => {
            currentProductIndex = (currentProductIndex < products.length - 1) ? currentProductIndex + 1 : 0;
            updateSlider();
        }, 3000);
    }

    prevButton.addEventListener('click', function() {
        currentProductIndex = (currentProductIndex > 0) ? currentProductIndex - 1 : products.length - 1;
        updateSlider();
        startSliderInterval(); // Reset the timer
    });

    nextButton.addEventListener('click', function() {
        currentProductIndex = (currentProductIndex < products.length - 1) ? currentProductIndex + 1 : 0;
        updateSlider();
        startSliderInterval(); // Reset the timer
    });

    // Initial setup
    updateSlider();
    startSliderInterval(); // Start the automatic changing
});


//JS FOR POP UP ERROR MESSAGE
// JS to show the pop-up on page load if there are messages
document.addEventListener("DOMContentLoaded", function() {
    const messages = document.querySelector(".messages");
    const popup = document.querySelector(".message-popup");
    const overlay = document.querySelector(".overlay");

    if (messages && messages.children.length > 0) { // Check if there are any messages
        overlay.style.display = 'block'; // Show overlay
        popup.style.display = 'block'; // Show pop-up
        document.getElementById('otp-modal').style.display = 'block';
    }

    // Hide the pop-up and overlay when the overlay is clicked
    overlay.addEventListener("click", function() {
        overlay.style.display = 'none';
        popup.style.display = 'none';
        document.getElementById('otp-modal').style.display = 'none';
    });
});
