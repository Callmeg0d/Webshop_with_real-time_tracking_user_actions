/**
 * Интеграция трекера с функционалом магазина
 * Отслеживание специфичных бизнес-событий
 */

(function() {
    'use strict';

    // Ждем инициализации трекера
    function waitForTracker(callback) {
        if (window.tracker) {
            callback();
        } else {
            setTimeout(() => waitForTracker(callback), 100);
        }
    }

    waitForTracker(function() {
        console.log('[Tracker Integrations] Initializing e-commerce tracking...');
         // Просмотр товара
        function trackProductView() {
            // Проверяем, находимся ли мы на странице товара
            const productPage = document.querySelector('[data-product-id]');
            if (productPage) {
                const productId = productPage.dataset.productId;
                const productName = productPage.dataset.productName;
                const productPrice = productPage.dataset.productPrice;
                const productCategory = productPage.dataset.productCategory;

                window.tracker.track('product_view', {
                    productId: productId,
                    productName: productName,
                    price: productPrice,
                    category: productCategory,
                    currency: 'RUB'
                });
            }
        }

         // Добавление в корзину
        function setupAddToCartTracking() {
            document.addEventListener('click', function(e) {
                const addToCartBtn = e.target.closest('[data-action="add-to-cart"]');
                if (addToCartBtn) {
                    const productId = addToCartBtn.dataset.productId;
                    const productName = addToCartBtn.dataset.productName;
                    const productPrice = addToCartBtn.dataset.productPrice;
                    const quantity = addToCartBtn.dataset.quantity || 1;

                    window.tracker.track('add_to_cart', {
                        productId: productId,
                        productName: productName,
                        price: productPrice,
                        quantity: quantity,
                        source: addToCartBtn.dataset.source || 'unknown',
                        currency: 'RUB'
                    });
                }
            });
        }

         //Удаление из корзины
        function setupRemoveFromCartTracking() {
            document.addEventListener('click', function(e) {
                const removeBtn = e.target.closest('[data-action="remove-from-cart"]');
                if (removeBtn) {
                    const productId = removeBtn.dataset.productId;
                    const productName = removeBtn.dataset.productName;

                    window.tracker.track('remove_from_cart', {
                        productId: productId,
                        productName: productName
                    });
                }
            });
        }

         //Просмотр корзины
        function trackCartView() {
            const cartPage = document.querySelector('[data-page="cart"]');
            if (cartPage) {
                const items = Array.from(document.querySelectorAll('[data-cart-item]')).map(item => ({
                    productId: item.dataset.productId,
                    productName: item.dataset.productName,
                    price: item.dataset.price,
                    quantity: item.dataset.quantity
                }));

                const totalValue = items.reduce((sum, item) => 
                    sum + (parseFloat(item.price) * parseInt(item.quantity)), 0
                );

                window.tracker.track('cart_view', {
                    items: items,
                    itemsCount: items.length,
                    totalValue: totalValue,
                    currency: 'RUB'
                });
            }
        }

         // Начало оформления заказа
        function setupCheckoutTracking() {
            document.addEventListener('click', function(e) {
                const checkoutBtn = e.target.closest('[data-action="checkout"]');
                if (checkoutBtn) {
                    const totalValue = checkoutBtn.dataset.totalValue;
                    const itemsCount = checkoutBtn.dataset.itemsCount;

                    window.tracker.track('checkout_started', {
                        totalValue: totalValue,
                        itemsCount: itemsCount,
                        currency: 'RUB'
                    });
                }
            });
        }

        // Завершение заказа
        function trackOrderComplete() {
            const orderConfirmation = document.querySelector('[data-order-id]');
            if (orderConfirmation) {
                const orderId = orderConfirmation.dataset.orderId;
                const totalValue = orderConfirmation.dataset.totalValue;
                const itemsCount = orderConfirmation.dataset.itemsCount;

                window.tracker.track('order_complete', {
                    orderId: orderId,
                    totalValue: totalValue,
                    itemsCount: itemsCount,
                    currency: 'RUB',
                    paymentMethod: orderConfirmation.dataset.paymentMethod || 'unknown'
                });
            }
        }

         //Отправка отзыва
        function setupReviewTracking() {
            const reviewForm = document.querySelector('[data-form="review"]');
            if (reviewForm) {
                reviewForm.addEventListener('submit', function(e) {
                    const productId = reviewForm.dataset.productId;
                    const rating = reviewForm.querySelector('[name="rating"]')?.value;

                    window.tracker.track('review_submitted', {
                        productId: productId,
                        rating: rating
                    });
                });
            }
        }

        // === ТРЕКИНГ ПОИСКА ===

        // Поиск товаров
        function setupSearchTracking() {
            const searchForm = document.querySelector('[data-form="search"]');
            if (searchForm) {
                searchForm.addEventListener('submit', function(e) {
                    const query = searchForm.querySelector('input[name="q"]')?.value;
                    
                    window.tracker.track('search', {
                        query: query,
                        queryLength: query?.length || 0
                    });
                });
            }

            // Трекинг результатов поиска
            const searchResults = document.querySelector('[data-search-results]');
            if (searchResults) {
                const query = searchResults.dataset.query;
                const resultsCount = searchResults.dataset.resultsCount;

                window.tracker.track('search_results', {
                    query: query,
                    resultsCount: resultsCount
                });
            }
        }

        //Вход пользователя
        function setupAuthTracking() {
            const loginForm = document.querySelector('[data-form="login"]');
            if (loginForm) {
                loginForm.addEventListener('submit', function(e) {
                    window.tracker.track('login_attempt', {
                        timestamp: Date.now()
                    });
                });
            }

            const registerForm = document.querySelector('[data-form="register"]');
            if (registerForm) {
                registerForm.addEventListener('submit', function(e) {
                    window.tracker.track('register_attempt', {
                        timestamp: Date.now()
                    });
                });
            }

            // Трекинг успешного входа (если есть индикатор)
            const authSuccess = document.querySelector('[data-auth-success]');
            if (authSuccess) {
                window.tracker.track('login_success', {
                    timestamp: Date.now()
                });
            }
        }

         // Быстрые множественные клики
        function setupRageClickTracking() {
            let clickCount = 0;
            let clickTimer;
            let lastClickTarget;

            document.addEventListener('click', function(e) {
                if (lastClickTarget === e.target) {
                    clickCount++;
                    
                    clearTimeout(clickTimer);
                    clickTimer = setTimeout(() => {
                        if (clickCount >= 3) {
                            window.tracker.track('rage_click', {
                                element: {
                                    tagName: e.target.tagName,
                                    id: e.target.id,
                                    className: e.target.className,
                                    text: e.target.innerText?.substring(0, 50)
                                },
                                clickCount: clickCount
                            });
                        }
                        clickCount = 0;
                        lastClickTarget = null;
                    }, 1000);
                } else {
                    clickCount = 1;
                    lastClickTarget = e.target;
                }
            });
        }

        // Инициализация всех трекингов
        function initializeAllTracking() {
            trackProductView();
            setupAddToCartTracking();
            setupRemoveFromCartTracking();
            trackCartView();
            setupCheckoutTracking();
            trackOrderComplete();
            setupReviewTracking();
            setupSearchTracking();
            setupFilterTracking();
            setupAuthTracking();
            setupRageClickTracking();

            console.log('[Tracker Integrations] E-commerce tracking initialized!');
        }

        // Запускаем после загрузки DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initializeAllTracking);
        } else {
            initializeAllTracking();
        }
    });

    window.TrackerIntegrations = {
        version: '1.0.0'
    };
})();

