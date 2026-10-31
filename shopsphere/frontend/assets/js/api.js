/**
 * Shall Shop API Client
 * Tagline: Discover More. Shop Better.
 * Centralized, secure Fetch abstraction communicating with Django REST Framework.
 */

const API_BASE = window.location.protocol === 'file:'
    ? 'http://127.0.0.1:8000/api/v1'
    : '/api/v1';

// Helper to get CSRF token from cookie
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

// Global cached CSRF token
let cachedCsrfToken = null;

async function ensureCsrfToken() {
    let token = getCookie('csrftoken');
    if (!token && !cachedCsrfToken) {
        try {
            const res = await fetch(`${API_BASE}/accounts/status/`, { credentials: 'include' });
            if (res.ok) {
                const data = await res.json();
                cachedCsrfToken = data.csrf_token;
            }
        } catch (e) {
            console.warn('Could not fetch CSRF token automatically:', e);
        }
    }
    return token || cachedCsrfToken || '';
}

async function apiRequest(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
    
    const headers = options.headers || {};
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }
    
    // Attach CSRF token for mutating requests
    const method = (options.method || 'GET').toUpperCase();
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
        const csrfToken = await ensureCsrfToken();
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
    }

    const config = {
        ...options,
        headers,
        credentials: 'include' // include session cookie for Django authentication
    };

    try {
        const response = await fetch(url, config);
        
        let data = null;
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        if (!response.ok) {
            const errorMessage = (data && typeof data === 'object')
                ? (data.error || data.detail || Object.values(data)[0] || 'An error occurred.')
                : (data || response.statusText);
            const err = new Error(Array.isArray(errorMessage) ? errorMessage.join(' ') : errorMessage);
            err.status = response.status;
            err.data = data;
            throw err;
        }

        return data;
    } catch (err) {
        throw err;
    }
}

// API Resource Modules
const API = {
    // Auth & Accounts
    auth: {
        status: () => apiRequest('/accounts/status/'),
        login: (credentials) => apiRequest('/accounts/login/', { method: 'POST', body: JSON.stringify(credentials) }),
        register: (payload) => apiRequest('/accounts/register/', { method: 'POST', body: JSON.stringify(payload) }),
        logout: () => apiRequest('/accounts/logout/', { method: 'POST' }),
        getProfile: () => apiRequest('/accounts/profile/'),
        updateProfile: (data) => apiRequest('/accounts/profile/', { method: 'PUT', body: JSON.stringify(data) }),
        changePassword: (data) => apiRequest('/accounts/change-password/', { method: 'POST', body: JSON.stringify(data) }),
        getAddresses: () => apiRequest('/accounts/addresses/'),
        addAddress: (data) => apiRequest('/accounts/addresses/', { method: 'POST', body: JSON.stringify(data) }),
        deleteAddress: (id) => apiRequest(`/accounts/addresses/${id}/`, { method: 'DELETE' }),
    },

    // Catalog & Products
    products: {
        list: (query = '') => apiRequest(`/products/${query ? (query.startsWith('?') ? query : '?' + query) : ''}`),
        detail: (slug) => apiRequest(`/products/${slug}/`),
        featured: () => apiRequest('/products/featured/'),
        trending: () => apiRequest('/products/trending/'),
        recommended: () => apiRequest('/products/recommended/'),
        newArrivals: () => apiRequest('/products/new_arrivals/'),
        bestSellers: () => apiRequest('/products/best_sellers/'),
        related: (slug) => apiRequest(`/products/${slug}/related/`),
        brands: () => apiRequest('/products/brands/'),
        categories: async () => {
            const res = await apiRequest('/products/categories/');
            return Array.isArray(res) ? res : (res.results || []);
        },
        create: (formData) => apiRequest('/products/', { method: 'POST', body: formData }),
        update: (slug, data) => apiRequest(`/products/${slug}/`, { method: 'PATCH', body: JSON.stringify(data) }),
        delete: (slug) => apiRequest(`/products/${slug}/`, { method: 'DELETE' }),
    },

    // Cart
    cart: {
        get: (shippingRule = 'standard') => apiRequest(`/cart/?shipping_rule=${shippingRule}`),
        add: (productId, quantity = 1) => apiRequest('/cart/items/', {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, quantity })
        }),
        update: (itemId, quantity) => apiRequest(`/cart/items/${itemId}/`, {
            method: 'PUT',
            body: JSON.stringify({ quantity })
        }),
        remove: (itemId) => apiRequest(`/cart/items/${itemId}/`, { method: 'DELETE' }),
        clear: () => apiRequest('/cart/', { method: 'DELETE' }),
        applyCoupon: (code) => apiRequest('/cart/coupon/', {
            method: 'POST',
            body: JSON.stringify({ code })
        }),
        removeCoupon: () => apiRequest('/cart/coupon/', { method: 'DELETE' }),
    },

    // Wishlist
    wishlist: {
        get: () => apiRequest('/wishlist/'),
        add: (productId) => apiRequest('/wishlist/', {
            method: 'POST',
            body: JSON.stringify({ product_id: productId })
        }),
        toggle: (productId) => apiRequest('/wishlist/', {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, toggle: true })
        }),
        remove: (productId) => apiRequest(`/wishlist/${productId}/`, { method: 'DELETE' }),
        moveToCart: (productId) => apiRequest(`/wishlist/${productId}/move-to-cart/`, { method: 'POST' }),
    },

    // Orders & Checkout
    orders: {
        checkout: (orderData) => apiRequest('/orders/checkout/', {
            method: 'POST',
            body: JSON.stringify(orderData)
        }),
        myOrders: () => apiRequest('/orders/my-orders/'),
        detail: (orderNumber, email = '') => apiRequest(`/orders/${orderNumber}/${email ? '?email=' + encodeURIComponent(email) : ''}`),
        cancel: (orderNumber) => apiRequest(`/orders/${orderNumber}/cancel/`, { method: 'POST' }),
    },

    // Payments
    payments: {
        verify: (orderNumber, transactionId = '') => apiRequest('/payments/verify/', {
            method: 'POST',
            body: JSON.stringify({ order_number: orderNumber, transaction_id: transactionId })
        }),
        config: () => apiRequest('/payments/config/'),
    },

    // Reviews
    reviews: {
        list: (productSlug = '') => apiRequest(`/reviews/${productSlug ? '?product=' + productSlug : ''}`),
        homepage: () => apiRequest('/reviews/homepage/'),
        create: (payload) => apiRequest('/reviews/', {
            method: 'POST',
            body: JSON.stringify(payload)
        }),
    },

    // Promotions
    promotions: {
        announcement: () => apiRequest('/promotions/announcement/'),
        newsletter: (email) => apiRequest('/promotions/newsletter/', {
            method: 'POST',
            body: JSON.stringify({ email })
        }),
        validateCoupon: (code, subtotal) => apiRequest('/promotions/validate-coupon/', {
            method: 'POST',
            body: JSON.stringify({ code, subtotal })
        }),
    },

    // Business Admin Dashboard
    admin: {
        metrics: () => apiRequest('/orders/dashboard/metrics/'),
        orders: (query = '') => apiRequest(`/orders/admin/manage/${query ? (query.startsWith('?') ? query : '?' + query) : ''}`),
        updateOrderStatus: (id, status, notes = '') => apiRequest(`/orders/admin/manage/${id}/update_status/`, {
            method: 'POST',
            body: JSON.stringify({ status, notes })
        }),
        exportCSVUrl: () => `${API_BASE}/orders/dashboard/export-csv/`,
        customers: (query = '') => apiRequest(`/accounts/admin/customers/${query ? (query.startsWith('?') ? query : '?' + query) : ''}`),
        products: (query = '') => apiRequest(`/products/?all=true${query ? '&' + query.replace(/^\?/, '') : ''}`),
        createProduct: (data) => apiRequest('/products/', { method: 'POST', body: JSON.stringify(data) }),
        updateProduct: (slug, data) => apiRequest(`/products/${slug}/`, { method: 'PATCH', body: JSON.stringify(data) }),
        deleteProduct: (slug) => apiRequest(`/products/${slug}/`, { method: 'DELETE' }),
        categories: async () => {
            const res = await apiRequest('/products/categories/');
            return Array.isArray(res) ? res : (res.results || []);
        },
        createCategory: (data) => apiRequest('/products/categories/', { method: 'POST', body: JSON.stringify(data) }),
        deleteCategory: (slug) => apiRequest(`/products/categories/${slug}/`, { method: 'DELETE' }),
        coupons: () => apiRequest('/promotions/admin/coupons/'),
        createCoupon: (data) => apiRequest('/promotions/admin/coupons/', { method: 'POST', body: JSON.stringify(data) }),
        deleteCoupon: (id) => apiRequest(`/promotions/admin/coupons/${id}/`, { method: 'DELETE' }),
    }
};

window.API = API;
