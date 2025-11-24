(function() {
    'use strict';

    class UserTracker {
        constructor(config = {}) {
            this.config = {
                debug: config.debug || false,
                trackClicks: config.trackClicks !== false,
                trackScrolls: config.trackScrolls !== false,
                trackPageViews: config.trackPageViews !== false,
                trackVisibility: config.trackVisibility !== false,
                scrollThrottle: config.scrollThrottle || 500,
                maxScrollDepth: 0
            };

            this.sessionId = this.generateSessionId();
            this.pageViewId = this.generatePageViewId();
            this.events = [];
            this.sessionStartTime = Date.now();
            this.pageLoadTime = Date.now();
            
            // Сохраняем viewport/screen один раз в сессию (не в каждом событии)
            this.sessionMetadata = {
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                },
                screen: {
                    width: window.screen.width,
                    height: window.screen.height
                },
                userAgent: navigator.userAgent
            };

            this.init();
        }

        init() {
            this.log('Tracker initialized', {
                sessionId: this.sessionId,
                pageViewId: this.pageViewId
            });

            // Трекинг загрузки страницы
            if (this.config.trackPageViews) {
                this.trackPageView();
            }

            // Трекинг кликов
            if (this.config.trackClicks) {
                this.setupClickTracking();
            }

            // Трекинг скроллов
            if (this.config.trackScrolls) {
                this.setupScrollTracking();
            }

            // Трекинг видимости страницы
            if (this.config.trackVisibility) {
                this.setupVisibilityTracking();
            }

            // Трекинг выхода со страницы
            this.setupBeforeUnloadTracking();
        }

        generateSessionId() {
            let sessionId = sessionStorage.getItem('tracker_session_id');
            if (!sessionId) {
                sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
                sessionStorage.setItem('tracker_session_id', sessionId);
            }
            return sessionId;
        }

        generatePageViewId() {
            return `pageview_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        }

        log(...args) {
            if (this.config.debug) {
                console.log('[UserTracker]', ...args);
            }
        }

        // Базовый метод для создания события
        createEvent(eventType, data = {}) {
            const event = {
                eventType: eventType,
                timestamp: Date.now(),
                sessionId: this.sessionId,
                pageViewId: this.pageViewId,
                url: window.location.href,
                pathname: window.location.pathname,
                referrer: document.referrer,
                // viewport/screen собираем только в первом событии сессии (в payload_json)
                ...data
            };

            this.events.push(event);
            this.log('Event tracked:', event);

            // Отправка при накоплении батча (каждые 20 событий)
            if (this.events.length >= 20) {
                this.sendEvents();
            }

            return event;
        }

        // Трекинг просмотра страницы
        trackPageView() {
            const event = this.createEvent('page_view', {
                title: document.title,
                loadTime: performance.timing ? 
                    performance.timing.loadEventEnd - performance.timing.navigationStart : null,
                sessionStartTime: this.sessionStartTime,
                ...this.sessionMetadata
            });

            // Трекинг времени на странице при выходе
            window.addEventListener('beforeunload', () => {
                this.trackTimeOnPage();
            });
        }

        // Трекинг времени на странице
        trackTimeOnPage() {
            const timeSpent = Date.now() - this.pageLoadTime;
            this.createEvent('page_time', {
                timeSpent: timeSpent,
                timeSpentSeconds: Math.round(timeSpent / 1000)
            });
        }

        // Трекинг кликов
        setupClickTracking() {
            document.addEventListener('click', (e) => {
                const target = e.target;
                const clickData = {
                    element: {
                        tagName: target.tagName,
                        id: target.id || null,
                        className: target.className || null,
                        text: target.innerText?.substring(0, 100) || null,
                        href: target.href || null
                    }
                };

                // Определяем тип клика
                if (target.tagName === 'A') {
                    clickData.clickType = 'link';
                    clickData.linkUrl = target.href;
                    clickData.linkText = target.innerText;
                } else if (target.tagName === 'BUTTON' || target.type === 'submit') {
                    clickData.clickType = 'button';
                    clickData.buttonText = target.innerText;
                } else if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
                    clickData.clickType = 'form_field';
                    clickData.inputType = target.type;
                    clickData.inputName = target.name;
                } else {
                    clickData.clickType = 'element';
                }

                this.createEvent('click', clickData);
            }, true);
        }

        // Трекинг скроллов
        setupScrollTracking() {
            // Собираем максимальную глубину при выходе со страницы
            window.addEventListener('scroll', () => {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                const scrollHeight = document.documentElement.scrollHeight;
                const clientHeight = document.documentElement.clientHeight;
                const scrollPercent = Math.round((scrollTop / (scrollHeight - clientHeight)) * 100);

                // Обновляем максимальную глубину прокрутки
                if (scrollPercent > this.config.maxScrollDepth) {
                    this.config.maxScrollDepth = scrollPercent;
                }
            }, { passive: true });

            // Трекинг максимальной глубины скролла при выходе
            window.addEventListener('beforeunload', () => {
                this.createEvent('scroll_depth', {
                    maxScrollDepth: this.config.maxScrollDepth
                });
            });
        }

        // Трекинг видимости страницы (переключение вкладок)
        setupVisibilityTracking() {
            let hiddenTime;

            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    hiddenTime = Date.now();
                    this.createEvent('page_hidden', {
                        timeOnPageBeforeHiding: hiddenTime - this.pageLoadTime
                    });
                } else {
                    const timeHidden = Date.now() - hiddenTime;
                    this.createEvent('page_visible', {
                        timeHidden: timeHidden,
                        timeHiddenSeconds: Math.round(timeHidden / 1000)
                    });
                }
            });
        }

        // Трекинг выхода со страницы
        setupBeforeUnloadTracking() {
            window.addEventListener('beforeunload', () => {
                this.createEvent('page_unload', {
                    totalTimeOnPage: Date.now() - this.pageLoadTime,
                    totalEvents: this.events.length,
                    maxScrollDepth: this.config.maxScrollDepth
                });

                // Отправляем события при выходе
                this.sendEvents();
            });

            // Периодическая отправка событий (каждые 10 секунд)
            setInterval(() => {
                if (this.events.length > 0) {
                    this.sendEvents();
                }
            }, 10000);
        }

        // Метод для отправки событий
        sendEvents() {
            if (this.events.length === 0) return;

            const eventsToSend = [...this.events];
            
            // Отправляем события батчами на бэкенд
            fetch("/analytics/events", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(eventsToSend),
                credentials: "include"
            }).then(() => {
                this.log(`Sent ${eventsToSend.length} events to server`);
            }).catch(err => {
                console.error("Failed to send events", err);
                // Не очищаем события при ошибке, чтобы попробовать отправить позже
            });

            // Очищаем отправленные события только после успешной отправки
            this.events = [];
        }

        // Публичный API для ручного трекинга кастомных событий
        track(eventName, data = {}) {
            this.createEvent(`custom_${eventName}`, data);
        }

        // Получить все собранные события
        getEvents() {
            return this.events;
        }

        // Очистить события
        clearEvents() {
            this.events = [];
            this.log('Events cleared');
        }

        // Получить информацию о текущей сессии
        getSessionInfo() {
            return {
                sessionId: this.sessionId,
                pageViewId: this.pageViewId,
                sessionDuration: Date.now() - this.sessionStartTime,
                pageViewDuration: Date.now() - this.pageLoadTime,
                eventsCount: this.events.length,
                maxScrollDepth: this.config.maxScrollDepth
            };
        }
    }

    // Инициализация трекера
    window.UserTracker = UserTracker;

    // Автоматическая инициализация при загрузке страницы
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.tracker = new UserTracker({
                debug: true, // Включаем debug режим для разработки
                trackClicks: true,
                trackScrolls: true,
                trackPageViews: true,
                trackVisibility: true
            });
        });
    } else {
        window.tracker = new UserTracker({
            debug: true,
            trackClicks: true,
            trackScrolls: true,
            trackPageViews: true,
            trackVisibility: true
        });
    }

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = UserTracker;
    }
})();

