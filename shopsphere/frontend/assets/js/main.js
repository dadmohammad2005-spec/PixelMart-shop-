/**
 * PixelMart Global Application Script
 * Tagline: MOBILE • LAPTOP • GADGETS
 * Location: Quetta, Balochistan (Contact: 00816-23-736822)
 * Orchestrates header state, notification toasts, cart/wishlist counters,
 * real-time search & brand filters, slide-out cart drawer, and bill printing.
 */

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initAnnouncementBar();
    initGlobalAuth();
    initHeaderSearch();
    initCartCounter();
    initWishlistCounter();
    initNewsletterForms();
    initNewArrivalsNav();
    initCartDrawerTriggers();
});

// Format Pakistani Rupee (PKR) e.g. PKR 70,000
function formatPKR(val) {
    const num = parseFloat(val);
    if (isNaN(num)) return 'PKR 0';
    return 'PKR ' + Math.round(num).toLocaleString('en-PK');
}
window.formatPKR = formatPKR;

// Theme Management (Light / Dark Mode)
function getPreferredTheme() {
    const saved = localStorage.getItem('pixelmart_theme') || localStorage.getItem('shall_shop_theme');
    if (saved) return saved;
    return (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
}

function applyTheme(theme) {
    const targetTheme = (theme === 'dark') ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', targetTheme);
    document.documentElement.setAttribute('data-bs-theme', targetTheme);
    if (document.body) {
        document.body.setAttribute('data-theme', targetTheme);
        document.body.setAttribute('data-bs-theme', targetTheme);
    }
    const icons = document.querySelectorAll('.theme-toggle-icon');
    icons.forEach(icon => {
        if (targetTheme === 'dark') {
            icon.className = 'bi bi-sun-fill theme-toggle-icon text-warning';
        } else {
            icon.className = 'bi bi-moon-stars-fill theme-toggle-icon text-primary';
        }
    });
}

function initTheme() {
    const initialTheme = getPreferredTheme();
    applyTheme(initialTheme);

    // Event delegation for theme switcher buttons
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.theme-toggle-btn');
        if (btn) {
            e.preventDefault();
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(nextTheme);
            localStorage.setItem('pixelmart_theme', nextTheme);
            localStorage.setItem('shall_shop_theme', nextTheme);
            showToast(`Switched to ${nextTheme === 'dark' ? 'Dark Mode 🌙' : 'Light Mode ☀️'}`, 'info');
        }
    });
}
window.initTheme = initTheme;
window.applyTheme = applyTheme;
window.getPreferredTheme = getPreferredTheme;

// Apply immediately on parse
try {
    applyTheme(getPreferredTheme());
} catch (e) {}

// Toast notification helper
function showToast(message, type = 'success') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1100';
        document.body.appendChild(container);
    }

    const toastId = 'toast_' + Math.random().toString(36).substring(2, 9);
    const bgClass = type === 'success' ? 'bg-success text-white' : type === 'error' ? 'bg-danger text-white' : 'bg-primary text-white';
    const icon = type === 'success' ? 'bi-check-circle-fill' : type === 'error' ? 'bi-exclamation-triangle-fill' : 'bi-info-circle-fill';

    const toastEl = document.createElement('div');
    toastEl.id = toastId;
    toastEl.className = `toast align-items-center ${bgClass} border-0 shadow-lg`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');

    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body d-flex align-items-center gap-2">
                <i class="bi ${icon}"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    container.appendChild(toastEl);
    const bsToast = new bootstrap.Toast(toastEl, { delay: 3500 });
    bsToast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}
window.showToast = showToast;

// Announcement Bar
async function initAnnouncementBar() {
    const el = document.getElementById('announcementBarContent');
    if (!el) return;
    try {
        const data = await API.promotions.announcement();
        if (data && data.message) {
            el.innerHTML = `<span>${data.message}</span>`;
            if (data.link_url) {
                el.innerHTML += `<a href="${data.link_url}" class="fw-bold">Learn More &rarr;</a>`;
            }
        }
    } catch (e) {
        // Fallback default
        el.innerHTML = '<span>⚡ <strong>PixelMart Quetta</strong> &bull; Genuine Laptops, Mobile Phones & Gadgets with 1-Year Local Warranty &bull; Hotline: <strong>00816-23-736822</strong></span>';
    }
}

// Global Auth State
async function initGlobalAuth() {
    try {
        const status = await API.auth.status();
        window.CURRENT_USER = status.user;
        window.IS_AUTHENTICATED = status.is_authenticated;
        renderHeaderAuth(status);
        if (status.is_authenticated) {
            initWishlistCounter();
        }
    } catch (e) {
        window.CURRENT_USER = null;
        window.IS_AUTHENTICATED = false;
        renderHeaderAuth({ is_authenticated: false });
    }
}

function renderHeaderAuth(status) {
    const userDropdown = document.getElementById('headerUserDropdown');
    const authLinks = document.getElementById('headerAuthLinks');
    const userNameSpan = document.getElementById('headerUserName');
    const adminLink = document.getElementById('headerAdminLink');

    if (status.is_authenticated && status.user) {
        if (authLinks) authLinks.classList.add('d-none');
        if (userDropdown) userDropdown.classList.remove('d-none');
        if (userNameSpan) userNameSpan.textContent = status.user.first_name || status.user.username;
        if (adminLink) {
            if (status.user.is_staff) {
                adminLink.classList.remove('d-none');
            } else {
                adminLink.classList.add('d-none');
            }
        }
    } else {
        if (userDropdown) userDropdown.classList.add('d-none');
        if (authLinks) authLinks.classList.remove('d-none');
        if (adminLink) adminLink.classList.add('d-none');
    }
}
window.initGlobalAuth = initGlobalAuth;

// Logout helper
async function handleLogout() {
    try {
        await API.auth.logout();
        showToast('Successfully logged out.', 'success');
        setTimeout(() => {
            window.location.href = window.location.pathname.includes('/pages/') ? 'login.html' : 'pages/login.html';
        }, 600);
    } catch (e) {
        showToast('Logout failed.', 'error');
    }
}
window.handleLogout = handleLogout;

// Cart Counter
async function initCartCounter() {
    try {
        const cart = await API.cart.get();
        updateCartBadge(cart.total_items || 0);
    } catch (e) {
        updateCartBadge(0);
    }
}

function updateCartBadge(count) {
    const badges = document.querySelectorAll('.cart-badge');
    badges.forEach(b => {
        b.textContent = count;
        if (count > 0) {
            b.classList.remove('d-none');
        } else {
            b.classList.add('d-none');
        }
    });
}
window.updateCartBadge = updateCartBadge;

// Wishlist Counter
async function initWishlistCounter() {
    if (!window.IS_AUTHENTICATED) {
        updateWishlistBadge(0);
        return;
    }
    try {
        const items = await API.wishlist.get();
        updateWishlistBadge(items.length || 0);
    } catch (e) {
        updateWishlistBadge(0);
    }
}

function updateWishlistBadge(count) {
    const badges = document.querySelectorAll('.wishlist-badge');
    badges.forEach(b => {
        b.textContent = count;
        if (count > 0) {
            b.classList.remove('d-none');
        } else {
            b.classList.add('d-none');
        }
    });
}
window.updateWishlistBadge = updateWishlistBadge;

// Header Search
function initHeaderSearch() {
    const searchForms = document.querySelectorAll('.header-search-form');
    searchForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const input = form.querySelector('input[type="search"]');
            if (input && input.value.trim()) {
                const term = encodeURIComponent(input.value.trim());
                const targetUrl = window.location.pathname.includes('/pages/')
                    ? `shop.html?search=${term}`
                    : `pages/shop.html?search=${term}`;
                window.location.href = targetUrl;
            }
        });
    });
}

// Newsletter
function initNewsletterForms() {
    const forms = document.querySelectorAll('.newsletter-form');
    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const input = form.querySelector('input[type="email"]');
            const submitBtn = form.querySelector('button[type="submit"]');
            if (!input || !input.value) return;

            const originalBtnText = submitBtn ? submitBtn.innerHTML : '';
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            }

            try {
                const res = await API.promotions.newsletter(input.value);
                showToast(res.message || 'Thank you for subscribing!', 'success');
                input.value = '';
            } catch (err) {
                showToast(err.message || 'Subscription failed. Please check the email.', 'error');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                }
            }
        });
    });
}

// Global card images cache for instant switcher
window.PRODUCT_CARD_IMAGES = window.PRODUCT_CARD_IMAGES || {};

// Shared Product Card Renderer for PixelMart with Brand, Specs, In-Stock, and PKR Price
function createProductCardHTML(p, basePath = 'pages/') {
    const detailLink = `${basePath}product-detail.html?slug=${p.slug}`;
    const saleBadge = p.is_on_sale
        ? `<span class="product-badge-discount">-${p.discount_percentage}% OFF</span>`
        : '';
    const originalPrice = p.is_on_sale
        ? `<span class="original-price-pkr">${formatPKR(p.price)}</span>`
        : '';
    const ratingStars = p.average_rating > 0
        ? `<div class="product-rating">
            <i class="bi bi-star-fill text-warning"></i>
            <span class="fw-semibold">${parseFloat(p.average_rating).toFixed(1)}</span>
            <span class="count text-muted">(${p.review_count || 1})</span>
          </div>`
        : `<div class="product-rating text-muted"><span class="count"><i class="bi bi-patch-check text-primary me-1"></i>Verified Spec</span></div>`;

    const outOfStock = !p.in_stock;
    const stockBadge = outOfStock
        ? `<span class="stock-pill out-of-stock mb-2"><i class="bi bi-x-circle-fill"></i> Out of Stock</span>`
        : `<span class="stock-pill in-stock mb-2"><i class="bi bi-check-circle-fill"></i> In Stock (${p.stock || 'Ready to Ship'})</span>`;

    // Extract all images for this card
    let images = [];
    if (Array.isArray(p.all_images) && p.all_images.length > 0) {
        images = p.all_images.filter(x => !!x);
    } else if (p.main_image) {
        images = [p.main_image];
    } else if (p.image_url) {
        images = [p.image_url];
    } else {
        images = [basePath.includes('pages/') ? '../assets/images/placeholder.jpg' : 'assets/images/placeholder.jpg'];
    }

    if (images.length === 0) {
        images = [basePath.includes('pages/') ? '../assets/images/placeholder.jpg' : 'assets/images/placeholder.jpg'];
    }

    // Cache images for interactive switching
    window.PRODUCT_CARD_IMAGES[p.id] = images;

    const hasMultiple = images.length > 1;
    const firstImg = images[0];

    // Build multi-image interactive elements
    let countBadgeHtml = '';
    let navArrowsHtml = '';
    let dotsHtml = '';

    if (hasMultiple) {
        countBadgeHtml = `
            <span class="card-img-count-badge" title="${images.length} photos available">
                <i class="bi bi-images me-1"></i>${images.length}
            </span>
        `;

        navArrowsHtml = `
            <button type="button" class="card-img-arrow prev" onclick="cycleCardImage(${p.id}, -1, event)" aria-label="Previous photo">
                <i class="bi bi-chevron-left"></i>
            </button>
            <button type="button" class="card-img-arrow next" onclick="cycleCardImage(${p.id}, 1, event)" aria-label="Next photo">
                <i class="bi bi-chevron-right"></i>
            </button>
        `;

        dotsHtml = `
            <div class="card-img-dots-container" onclick="event.stopPropagation()">
                <div class="card-img-dots">
                    ${images.map((img, idx) => `
                        <span class="card-img-dot ${idx === 0 ? 'active' : ''}" 
                              data-idx="${idx}" 
                              onmouseenter="setCardImage(${p.id}, ${idx}, event)" 
                              onclick="setCardImage(${p.id}, ${idx}, event)" 
                              title="Photo ${idx + 1} of ${images.length}"></span>
                    `).join('')}
                </div>
            </div>
        `;
    }

    const brandBadge = p.brand ? `<span class="product-brand-tag">${p.brand}</span>` : '';
    const specsSnippet = p.specs
        ? `<div class="product-specs-snippet" title="${p.specs}"><i class="bi bi-cpu me-1"></i>${p.specs}</div>`
        : `<div class="product-specs-snippet text-muted small"><i class="bi bi-shield-check me-1"></i>100% Genuine Tested • Quetta Showroom</div>`;

    return `
        <div class="col-12 col-sm-6 col-lg-3 mb-4 product-grid-item" data-brand="${p.brand || ''}" data-name="${(p.name || '').toLowerCase()}" data-specs="${(p.specs || '').toLowerCase()}" data-category="${p.category_slug || ''}">
            <div class="product-card h-100 d-flex flex-column" id="productCard_${p.id}">
                <div class="product-image-container" id="cardImgContainer_${p.id}" data-current-index="0">
                    ${saleBadge}
                    ${countBadgeHtml}
                    <button type="button" class="product-wishlist-btn" onclick="toggleWishlist(${p.id}, this)" title="Add to Wishlist" aria-label="Add to Wishlist">
                        <i class="bi bi-heart"></i>
                    </button>
                    <a href="${detailLink}" class="product-image-link d-block w-100 h-100">
                        <img src="${firstImg}" 
                             id="cardImg_${p.id}" 
                             alt="${p.name}" 
                             class="product-image" 
                             loading="lazy" 
                             onerror="this.src='https://placehold.co/600x600/f1f5f9/0f172a?text=${encodeURIComponent(p.name)}'">
                    </a>
                    ${navArrowsHtml}
                    ${dotsHtml}
                </div>
                <div class="product-card-body d-flex flex-column flex-grow-1">
                    <div class="d-flex align-items-center justify-content-between mb-1">
                        <div>
                            ${brandBadge}
                            <span class="product-category-meta">${p.category_name || 'Hardware'}</span>
                        </div>
                    </div>
                    <h3 class="product-title mb-1">
                        <a href="${detailLink}" class="text-reset text-decoration-none">${p.name}</a>
                    </h3>
                    ${specsSnippet}
                    <div class="d-flex align-items-center justify-content-between mb-2">
                        ${stockBadge}
                        ${ratingStars}
                    </div>
                    <div class="product-price-row mt-auto mb-3">
                        <span class="current-price-pkr">${formatPKR(p.current_price)}</span>
                        ${originalPrice}
                    </div>
                    <button type="button" class="btn btn-primary btn-add-cart w-100" ${outOfStock ? 'disabled' : ''} onclick="handleQuickAdd(${p.id}, this)">
                        <i class="bi bi-cart-plus me-1"></i> ${outOfStock ? 'Out of Stock' : 'Add to Cart'}
                    </button>
                </div>
            </div>
        </div>
    `;
}
window.createProductCardHTML = createProductCardHTML;

// Switch product card image to specific index
function setCardImage(productId, index, event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    const images = window.PRODUCT_CARD_IMAGES[productId];
    if (!images || !images[index]) return;

    const imgEl = document.getElementById(`cardImg_${productId}`);
    const container = document.getElementById(`cardImgContainer_${productId}`);
    if (!imgEl) return;

    imgEl.style.opacity = '0.35';
    setTimeout(() => {
        imgEl.src = images[index];
        imgEl.style.opacity = '1';
    }, 70);

    if (container) {
        container.setAttribute('data-current-index', index);
        const dots = container.querySelectorAll('.card-img-dot');
        dots.forEach((dot, idx) => {
            if (idx === index) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }
}
window.setCardImage = setCardImage;

// Cycle product card image by delta (+1 next, -1 prev)
function cycleCardImage(productId, delta, event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    const images = window.PRODUCT_CARD_IMAGES[productId];
    if (!images || images.length <= 1) return;

    const container = document.getElementById(`cardImgContainer_${productId}`);
    let currentIndex = parseInt(container?.getAttribute('data-current-index') || '0', 10);
    currentIndex = (currentIndex + delta + images.length) % images.length;
    setCardImage(productId, currentIndex, event);
}
window.cycleCardImage = cycleCardImage;

// Quick Add to Cart Handler (Automatically slides open the Cart Drawer)
async function handleQuickAdd(productId, btn) {
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Adding...';

    try {
        const res = await API.cart.add(productId, 1);
        updateCartBadge(res.cart.total_items);
        showToast(res.message || 'Item added to shopping cart!', 'success');
        openCartDrawer();
    } catch (e) {
        showToast(e.message || 'Could not add to cart.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}
window.handleQuickAdd = handleQuickAdd;

/* ==========================================================================
   SLIDE-OUT CART DRAWER IMPLEMENTATION
   ========================================================================== */

function getPagesBase() {
    return window.location.pathname.includes('/pages/') ? '' : 'pages/';
}

function ensureCartDrawer() {
    if (document.getElementById('cartDrawer')) return;

    const overlay = document.createElement('div');
    overlay.id = 'cartDrawerOverlay';
    overlay.className = 'cart-drawer-overlay';
    overlay.onclick = closeCartDrawer;

    const drawer = document.createElement('div');
    drawer.id = 'cartDrawer';
    drawer.className = 'cart-drawer';
    drawer.innerHTML = `
        <div class="cart-drawer-header">
            <h5><i class="bi bi-cart3 text-primary"></i> Cart Summary (<span id="cartDrawerCount">0</span>)</h5>
            <button type="button" class="cart-drawer-close" onclick="closeCartDrawer()" aria-label="Close cart drawer">
                <i class="bi bi-x-lg"></i>
            </button>
        </div>
        <div class="cart-drawer-body" id="cartDrawerBody">
            <div class="text-center py-5 text-muted">
                <div class="spinner-border spinner-border-sm text-primary mb-2"></div>
                <p class="small">Loading cart items...</p>
            </div>
        </div>
        <div class="cart-drawer-footer" id="cartDrawerFooter">
            <div class="cart-drawer-summary-row">
                <span>Subtotal</span>
                <strong id="cartDrawerSubtotal">PKR 0</strong>
            </div>
            <div class="cart-drawer-summary-row text-success d-none" id="cartDrawerDiscountRow">
                <span>Discount</span>
                <strong id="cartDrawerDiscount">-PKR 0</strong>
            </div>
            <div class="cart-drawer-summary-row">
                <span>Quetta Delivery</span>
                <span class="text-success fw-semibold" id="cartDrawerShipping">FREE in Quetta</span>
            </div>
            <div class="cart-drawer-summary-total">
                <span>Estimated Total</span>
                <span class="total-amount" id="cartDrawerTotal">PKR 0</span>
            </div>
            <div class="cart-drawer-actions">
                <a href="${getPagesBase()}checkout.html" class="btn btn-primary w-100 py-2 fw-semibold">
                    Proceed to Checkout <i class="bi bi-arrow-right ms-1"></i>
                </a>
                <a href="${getPagesBase()}cart.html" class="btn btn-outline-secondary w-100 py-2 small">
                    View & Edit Full Cart
                </a>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);
    document.body.appendChild(drawer);
}

async function openCartDrawer() {
    ensureCartDrawer();
    const overlay = document.getElementById('cartDrawerOverlay');
    const drawer = document.getElementById('cartDrawer');
    if (overlay) overlay.classList.add('active');
    if (drawer) drawer.classList.add('open');
    document.body.style.overflow = 'hidden';
    await renderCartDrawer();
}

function closeCartDrawer() {
    const overlay = document.getElementById('cartDrawerOverlay');
    const drawer = document.getElementById('cartDrawer');
    if (overlay) overlay.classList.remove('active');
    if (drawer) drawer.classList.remove('open');
    document.body.style.overflow = '';
}

function toggleCartDrawer() {
    const drawer = document.getElementById('cartDrawer');
    if (drawer && drawer.classList.contains('open')) {
        closeCartDrawer();
    } else {
        openCartDrawer();
    }
}
window.openCartDrawer = openCartDrawer;
window.closeCartDrawer = closeCartDrawer;
window.toggleCartDrawer = toggleCartDrawer;

async function renderCartDrawer() {
    ensureCartDrawer();
    const body = document.getElementById('cartDrawerBody');
    const countEl = document.getElementById('cartDrawerCount');
    const footer = document.getElementById('cartDrawerFooter');

    try {
        const cart = await API.cart.get();
        const items = cart.items || [];
        const totalItems = cart.total_items || 0;
        if (countEl) countEl.textContent = totalItems;
        updateCartBadge(totalItems);

        if (items.length === 0) {
            body.innerHTML = `
                <div class="text-center py-5">
                    <i class="bi bi-bag-x fs-1 text-muted mb-3 d-block"></i>
                    <h6 class="fw-bold">Your cart is empty</h6>
                    <p class="small text-muted mb-4">Add your favorite laptop or mobile phone to get started!</p>
                    <a href="${getPagesBase()}shop.html" class="btn btn-sm btn-outline-primary" onclick="closeCartDrawer()">
                        Browse PixelMart Catalog
                    </a>
                </div>
            `;
            if (footer) footer.classList.add('d-none');
            return;
        }

        if (footer) footer.classList.remove('d-none');

        body.innerHTML = items.map(item => `
            <div class="cart-drawer-item" id="drawerItem_${item.id}">
                <img src="${item.product.main_image || getPagesBase() + '../assets/images/placeholder.jpg'}" alt="${item.product.name}" onerror="this.src='https://placehold.co/120x120/f1f5f9/0f172a?text=PixelMart'">
                <div class="cart-drawer-item-info">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="cart-drawer-item-title" title="${item.product.name}">${item.product.name}</div>
                        <button type="button" class="cart-drawer-item-remove ms-1" onclick="removeDrawerItem(${item.id})" title="Remove">
                            <i class="bi bi-trash3"></i>
                        </button>
                    </div>
                    <div class="cart-drawer-item-specs">${item.product.brand ? '<strong>' + item.product.brand + '</strong> &bull; ' : ''}${item.product.specs || ''}</div>
                    <div class="d-flex justify-content-between align-items-center mt-1">
                        <div class="cart-drawer-qty-control">
                            <button type="button" class="cart-drawer-qty-btn" onclick="updateDrawerItemQty(${item.id}, ${item.quantity - 1})">-</button>
                            <input type="text" readonly class="cart-drawer-qty-input" value="${item.quantity}">
                            <button type="button" class="cart-drawer-qty-btn" onclick="updateDrawerItemQty(${item.id}, ${item.quantity + 1})">+</button>
                        </div>
                        <div class="cart-drawer-item-price">${formatPKR(item.line_total)}</div>
                    </div>
                </div>
            </div>
        `).join('');

        // Update totals
        const totals = cart.totals || {};
        document.getElementById('cartDrawerSubtotal').textContent = formatPKR(totals.subtotal || 0);
        document.getElementById('cartDrawerTotal').textContent = formatPKR(totals.grand_total || totals.subtotal || 0);

        const discountRow = document.getElementById('cartDrawerDiscountRow');
        if (discountRow) {
            if (totals.discount_amount && parseFloat(totals.discount_amount) > 0) {
                discountRow.classList.remove('d-none');
                document.getElementById('cartDrawerDiscount').textContent = '-' + formatPKR(totals.discount_amount);
            } else {
                discountRow.classList.add('d-none');
            }
        }
    } catch (e) {
        body.innerHTML = `
            <div class="text-center py-4 text-danger small">
                <i class="bi bi-exclamation-triangle fs-3 d-block mb-1"></i>
                Could not load cart. Please retry.
            </div>
        `;
    }
}
window.renderCartDrawer = renderCartDrawer;

async function updateDrawerItemQty(itemId, newQty) {
    if (newQty <= 0) {
        return removeDrawerItem(itemId);
    }
    try {
        await API.cart.update(itemId, newQty);
        await renderCartDrawer();
    } catch (e) {
        showToast(e.message || 'Could not update quantity', 'error');
    }
}
window.updateDrawerItemQty = updateDrawerItemQty;

async function removeDrawerItem(itemId) {
    try {
        await API.cart.remove(itemId);
        showToast('Item removed from cart', 'info');
        await renderCartDrawer();
    } catch (e) {
        showToast(e.message || 'Could not remove item', 'error');
    }
}
window.removeDrawerItem = removeDrawerItem;

// Intercept header cart buttons to open the cart drawer smoothly
function initCartDrawerTriggers() {
    ensureCartDrawer();
    document.addEventListener('click', (e) => {
        const cartBtn = e.target.closest('.header-cart-drawer-btn, [data-open-cart-drawer="true"]');
        if (cartBtn) {
            e.preventDefault();
            toggleCartDrawer();
        }
    });
}


// Toggle Wishlist Handler
async function toggleWishlist(productId, btn) {
    if (!window.IS_AUTHENTICATED) {
        showToast('Please sign in to add products to your wishlist.', 'info');
        const loginUrl = window.location.pathname.includes('/pages/') ? 'login.html' : 'pages/login.html';
        setTimeout(() => window.location.href = loginUrl, 1200);
        return;
    }

    try {
        const res = await API.wishlist.toggle(productId);
        const icon = btn.querySelector('i');
        if (res.in_wishlist) {
            btn.classList.add('active');
            if (icon) {
                icon.className = 'bi bi-heart-fill text-danger';
            }
            showToast(res.message || 'Added to wishlist!', 'success');
        } else {
            btn.classList.remove('active');
            if (icon) {
                icon.className = 'bi bi-heart';
            }
            showToast(res.message || 'Removed from wishlist.', 'info');
        }
        initWishlistCounter();
    } catch (e) {
        showToast(e.message || 'Failed to update wishlist.', 'error');
    }
}
window.toggleWishlist = toggleWishlist;

// New Arrivals Automatic Home Navigation & Smooth Scroll
function initNewArrivalsNav() {
    // 1. If arriving on page with #newArrivalsSection in hash
    if (window.location.hash === '#newArrivalsSection' || window.location.hash.toLowerCase().includes('newarrivals')) {
        setTimeout(() => {
            scrollToNewArrivals();
        }, 350);
    }

    // 2. Delegate click on any New Arrivals anchor link
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;
        const href = link.getAttribute('href');
        if (href && (href === '#newArrivalsSection' || href.endsWith('#newArrivalsSection'))) {
            const isHomePage = window.location.pathname === '/' ||
                               window.location.pathname.endsWith('/index.html') ||
                               window.location.pathname.endsWith('index.html') ||
                               window.location.pathname === '/index' ||
                               window.location.pathname === '/home';
            if (isHomePage) {
                e.preventDefault();
                history.pushState(null, null, '#newArrivalsSection');
                scrollToNewArrivals();
            }
        }
    });
}

function scrollToNewArrivals() {
    const el = document.getElementById('newArrivalsSection');
    if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        el.classList.add('section-highlight-pulse');
        setTimeout(() => el.classList.remove('section-highlight-pulse'), 2800);
    }
}
window.initNewArrivalsNav = initNewArrivalsNav;
window.scrollToNewArrivals = scrollToNewArrivals;
