// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

// Global state
let cart = JSON.parse(localStorage.getItem('cart')) || [];
let temples = [];
let prasadamItems = [];

// DOM Elements
const templesContainer = document.getElementById('temples-container');
const prasadamContainer = document.getElementById('prasadam-container');
const cartItemsContainer = document.getElementById('cart-items');
const cartCountElement = document.getElementById('cart-count');
const cartTotalElement = document.getElementById('cart-total');
const emptyCartMessage = document.getElementById('empty-cart-message');
const cartSidebar = document.getElementById('cart-sidebar');
const cartOverlay = document.getElementById('cart-overlay');
const cartToggle = document.getElementById('cart-toggle');
const closeCart = document.getElementById('close-cart');
const checkoutBtn = document.getElementById('checkout-btn');
const checkoutModal = document.getElementById('checkout-modal');
const closeModal = document.getElementById('close-modal');
const checkoutForm = document.getElementById('checkout-form');
const orderItemsSummary = document.getElementById('order-items-summary');
const orderTotalElement = document.getElementById('order-total');
const filterButtons = document.querySelectorAll('.filter-btn');

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    loadTemples();
    loadPrasadam();
    updateCartCount();
    renderCartItems();
    
    // Event listeners
    cartToggle.addEventListener('click', toggleCart);
    closeCart.addEventListener('click', closeCartSidebar);
    cartOverlay.addEventListener('click', closeCartSidebar);
    checkoutBtn.addEventListener('click', openCheckoutModal);
    closeModal.addEventListener('click', closeCheckoutModal);
    
    // Filter buttons
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filter temples
            const filter = this.getAttribute('data-filter');
            filterTemples(filter);
        });
    });
    
    // Form submission
    checkoutForm.addEventListener('submit', placeOrder);
    
    // Mobile menu toggle
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    hamburger.addEventListener('click', function() {
        navMenu.classList.toggle('active');
        hamburger.classList.toggle('active');
    });
});

// Load temples from API
async function loadTemples() {
    try {
        const response = await fetch(`${API_BASE_URL}/temples`);
        temples = await response.json();
        renderTemples(temples);
    } catch (error) {
        console.error('Error loading temples:', error);
        templesContainer.innerHTML = '<p class="error">Failed to load temples. Please try again later.</p>';
    }
}

// Load prasadam from API
async function loadPrasadam() {
    try {
        const response = await fetch(`${API_BASE_URL}/prasadam`);
        prasadamItems = await response.json();
        renderPrasadam(prasadamItems);
    } catch (error) {
        console.error('Error loading prasadam:', error);
        prasadamContainer.innerHTML = '<p class="error">Failed to load prasadam items. Please try again later.</p>';
    }
}

// Render temples to the DOM
function renderTemples(templesArray) {
    templesContainer.innerHTML = '';
    
    templesArray.forEach(temple => {
        const templeCard = document.createElement('div');
        templeCard.className = 'temple-card';
        
        const typeColor = temple.type === 'jyotirlinga' ? '#8B4513' : '#D2691E';
        const typeText = temple.type === 'jyotirlinga' ? 'Jyotirlinga' : 'Dham';
        
        templeCard.innerHTML = `
            <div class="temple-header" style="background-color: ${typeColor}">
                <h3>${temple.name}</h3>
                <span class="temple-type">${typeText}</span>
            </div>
            <div class="temple-body">
                <p class="temple-location">
                    <i class="fas fa-map-marker-alt"></i> ${temple.location}
                </p>
                <p class="temple-description">${temple.description}</p>
                <button class="btn-secondary view-prasadam" data-temple-id="${temple.id}">
                    View Prasadam
                </button>
            </div>
        `;
        
        templesContainer.appendChild(templeCard);
    });
    
    // Add event listeners to view prasadam buttons
    document.querySelectorAll('.view-prasadam').forEach(button => {
        button.addEventListener('click', function() {
            const templeId = this.getAttribute('data-temple-id');
            filterPrasadamByTemple(templeId);
            
            // Scroll to prasadam section
            document.getElementById('prasadam').scrollIntoView({ behavior: 'smooth' });
        });
    });
}

// Render prasadam to the DOM
function renderPrasadam(prasadamArray) {
    prasadamContainer.innerHTML = '';
    
    prasadamArray.forEach(item => {
        const prasadamCard = document.createElement('div');
        prasadamCard.className = 'prasadam-card';
        
        const icon = item.temple_type === 'jyotirlinga' ? 'fas fa-fire' : 'fas fa-temple';
        
        prasadamCard.innerHTML = `
            <div class="prasadam-image">
                <i class="${icon}"></i>
            </div>
            <div class="prasadam-content">
                <h3>${item.name}</h3>
                <p class="prasadam-temple">From: ${item.temple_name}</p>
                <p class="prasadam-description">${item.description}</p>
                <div class="prasadam-footer">
                    <div class="prasadam-price">₹${item.price}</div>
                    <button class="add-to-cart" data-id="${item.id}" data-name="${item.name}" 
                            data-price="${item.price}" data-temple="${item.temple_name}">
                        <i class="fas fa-cart-plus"></i> Add to Cart
                    </button>
                </div>
            </div>
        `;
        
        prasadamContainer.appendChild(prasadamCard);
    });
    
    // Add event listeners to add to cart buttons
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            const item = {
                id: this.getAttribute('data-id'),
                name: this.getAttribute('data-name'),
                price: parseFloat(this.getAttribute('data-price')),
                temple: this.getAttribute('data-temple'),
                quantity: 1
            };
            
            addToCart(item);
            
            // Visual feedback
            this.innerHTML = '<i class="fas fa-check"></i> Added!';
            this.style.backgroundColor = '#4CAF50';
            
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
                this.style.backgroundColor = '';
            }, 1500);
        });
    });
}

// Filter temples by type
function filterTemples(filter) {
    if (filter === 'all') {
        renderTemples(temples);
    } else {
        const filteredTemples = temples.filter(temple => temple.type === filter);
        renderTemples(filteredTemples);
    }
}

// Filter prasadam by temple
async function filterPrasadamByTemple(templeId) {
    try {
        const response = await fetch(`${API_BASE_URL}/temples/${templeId}/prasadam`);
        const templePrasadam = await response.json();
        renderPrasadam(templePrasadam);
    } catch (error) {
        console.error('Error filtering prasadam:', error);
    }
}

// Cart functionality
function addToCart(item) {
    // Check if item already in cart
    const existingItem = cart.find(cartItem => cartItem.id === item.id);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push(item);
    }
    
    // Update UI and localStorage
    updateCartCount();
    renderCartItems();
    saveCartToLocalStorage();
    
    // Open cart sidebar
    if (!cartSidebar.classList.contains('active')) {
        openCartSidebar();
    }
}

function removeFromCart(itemId) {
    cart = cart.filter(item => item.id !== itemId);
    
    // Update UI and localStorage
    updateCartCount();
    renderCartItems();
    saveCartToLocalStorage();
}

function updateCartCount() {
    const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
    cartCountElement.textContent = totalItems;
}

function renderCartItems() {
    cartItemsContainer.innerHTML = '';
    
    if (cart.length === 0) {
        emptyCartMessage.style.display = 'block';
        checkoutBtn.disabled = true;
        cartTotalElement.textContent = '₹0';
        return;
    }
    
    emptyCartMessage.style.display = 'none';
    checkoutBtn.disabled = false;
    
    let total = 0;
    
    cart.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.className = 'cart-item';
        
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        
        itemElement.innerHTML = `
            <div class="cart-item-info">
                <h4>${item.name}</h4>
                <p class="cart-item-temple">${item.temple}</p>
                <p>Quantity: ${item.quantity} × ₹${item.price}</p>
            </div>
            <div class="cart-item-right">
                <div class="cart-item-price">₹${itemTotal.toFixed(2)}</div>
                <button class="cart-item-remove" data-id="${item.id}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        cartItemsContainer.appendChild(itemElement);
    });
    
    // Update total
    cartTotalElement.textContent = `₹${total.toFixed(2)}`;
    
    // Add event listeners to remove buttons
    document.querySelectorAll('.cart-item-remove').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-id');
            removeFromCart(itemId);
        });
    });
}

function saveCartToLocalStorage() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

// Cart sidebar functions
function toggleCart() {
    cartSidebar.classList.toggle('active');
    cartOverlay.classList.toggle('active');
}

function openCartSidebar() {
    cartSidebar.classList.add('active');
    cartOverlay.classList.add('active');
}

function closeCartSidebar() {
    cartSidebar.classList.remove('active');
    cartOverlay.classList.remove('active');
}

// Checkout modal functions
function openCheckoutModal() {
    if (cart.length === 0) return;
    
    // Update order summary
    updateOrderSummary();
    
    // Show modal
    checkoutModal.classList.add('active');
    closeCartSidebar();
}

function closeCheckoutModal() {
    checkoutModal.classList.remove('active');
}

function updateOrderSummary() {
    orderItemsSummary.innerHTML = '';
    
    let total = 0;
    
    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        
        const itemElement = document.createElement('div');
        itemElement.className = 'order-item-summary';
        itemElement.innerHTML = `
            <span>${item.name} (${item.quantity})</span>
            <span>₹${itemTotal.toFixed(2)}</span>
        `;
        
        orderItemsSummary.appendChild(itemElement);
    });
    
    orderTotalElement.textContent = `₹${total.toFixed(2)}`;
}

// Place order function
async function placeOrder(e) {
    e.preventDefault();
    
    // Get form data
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const address = document.getElementById('address').value;
    
    // Calculate total
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    // Prepare order data
    const orderData = {
        user_name: name,
        user_email: email,
        user_phone: phone,
        user_address: address,
        items: JSON.stringify(cart),
        total_amount: total
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/order`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Show success message
            alert(`Order placed successfully! Your order ID is: ${result.order_id}`);
            
            // Clear cart
            cart = [];
            saveCartToLocalStorage();
            updateCartCount();
            renderCartItems();
            
            // Close modal and reset form
            closeCheckoutModal();
            checkoutForm.reset();
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            alert(`Failed to place order: ${result.error}`);
        }
    } catch (error) {
        console.error('Error placing order:', error);
        alert('Failed to place order. Please try again.');
    }
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            // Close mobile menu if open
            const navMenu = document.querySelector('.nav-menu');
            const hamburger = document.querySelector('.hamburger');
            navMenu.classList.remove('active');
            hamburger.classList.remove('active');
            
            // Scroll to target
            targetElement.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});