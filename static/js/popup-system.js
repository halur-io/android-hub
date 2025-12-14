(function() {
    'use strict';
    
    var SitePopup = {
        config: null,
        shown: {},
        
        // Push event to Google Tag Manager dataLayer
        pushGTMEvent: function(eventName, eventData) {
            if (typeof window.dataLayer !== 'undefined') {
                window.dataLayer.push({
                    'event': eventName,
                    ...eventData
                });
            }
        },
        
        init: function(popupConfigs) {
            console.log('[Popup] init called with', popupConfigs ? popupConfigs.length : 0, 'popups');
            if (!popupConfigs || !popupConfigs.length) return;
            
            this.loadShownState();
            console.log('[Popup] Shown state:', this.shown);
            
            var self = this;
            popupConfigs.sort(function(a, b) { return b.priority - a.priority; });
            
            popupConfigs.forEach(function(config) {
                console.log('[Popup] Checking popup', config.id, '- shouldShow:', self.shouldShow(config));
                if (self.shouldShow(config)) {
                    console.log('[Popup] Scheduling popup', config.id, 'trigger:', config.trigger_type);
                    self.schedulePopup(config);
                } else {
                    console.log('[Popup] Popup', config.id, 'will not show - checkDevice:', self.checkDevice(config), 'freq:', config.show_frequency);
                }
            });
        },
        
        loadShownState: function() {
            try {
                var stored = localStorage.getItem('popup_shown');
                this.shown = stored ? JSON.parse(stored) : {};
            } catch(e) {
                this.shown = {};
            }
        },
        
        saveShownState: function() {
            try {
                localStorage.setItem('popup_shown', JSON.stringify(this.shown));
            } catch(e) {}
        },
        
        shouldShow: function(config) {
            var id = config.id;
            var freq = config.show_frequency;
            var now = Date.now();
            var lastShown = this.shown[id];
            
            if (!this.checkDevice(config)) return false;
            
            if (freq === 'always') return true;
            
            if (freq === 'once_per_session') {
                return !sessionStorage.getItem('popup_' + id);
            }
            
            if (freq === 'once_ever') {
                return !lastShown;
            }
            
            if (freq === 'once_per_day') {
                if (!lastShown) return true;
                var dayMs = 24 * 60 * 60 * 1000;
                return (now - lastShown) > dayMs;
            }
            
            if (freq === 'every_x_days') {
                if (!lastShown) return true;
                var days = config.show_every_x_days || 1;
                return (now - lastShown) > (days * 24 * 60 * 60 * 1000);
            }
            
            return true;
        },
        
        checkDevice: function(config) {
            var width = window.innerWidth;
            if (width >= 1024 && !config.show_on_desktop) return false;
            if (width >= 768 && width < 1024 && !config.show_on_tablet) return false;
            if (width < 768 && !config.show_on_mobile) return false;
            return true;
        },
        
        schedulePopup: function(config) {
            var self = this;
            var trigger = config.trigger_type;
            
            if (trigger === 'immediate') {
                this.showPopup(config);
            } else if (trigger === 'time_delay') {
                var delay = (config.show_delay_seconds || 3) * 1000;
                setTimeout(function() {
                    self.showPopup(config);
                }, delay);
            } else if (trigger === 'scroll') {
                var scrollHandler = function() {
                    var scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
                    if (scrollPercent >= (config.scroll_percentage || 50)) {
                        window.removeEventListener('scroll', scrollHandler);
                        self.showPopup(config);
                    }
                };
                window.addEventListener('scroll', scrollHandler);
            } else if (trigger === 'exit_intent') {
                var exitHandler = function(e) {
                    if (e.clientY <= 0) {
                        document.removeEventListener('mouseout', exitHandler);
                        self.showPopup(config);
                    }
                };
                document.addEventListener('mouseout', exitHandler);
            }
        },
        
        showPopup: function(config) {
            var self = this;
            var lang = document.documentElement.lang || 'he';
            var isHe = lang === 'he';
            var isMobile = window.innerWidth < 768;
            
            var overlay = document.createElement('div');
            overlay.className = 'site-popup-overlay';
            overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:' + (config.overlay_color || 'rgba(0,0,0,0.5)') + ';z-index:99999;display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity ' + (config.animation_duration || 300) + 'ms;padding:2vh 2vw;box-sizing:border-box;';
            
            var popup = document.createElement('div');
            popup.className = 'site-popup';
            
            var position = config.popup_position || 'center';
            var size = config.popup_size || 'medium';
            
            // Mobile-first responsive sizes using viewport units only
            var sizeStyles;
            if (isMobile) {
                // Mobile: max 92vw width, max 35vh height, no fullscreen
                sizeStyles = {
                    small: 'max-width:85vw;',
                    medium: 'max-width:92vw;',
                    large: 'max-width:92vw;',
                    fullscreen: 'max-width:92vw;' // Prevent fullscreen on mobile
                };
            } else {
                sizeStyles = {
                    small: 'max-width:min(350px, 80vw);',
                    medium: 'max-width:min(500px, 85vw);',
                    large: 'max-width:min(700px, 90vw);',
                    fullscreen: 'max-width:min(700px, 90vw);' // Prevent fullscreen
                };
            }
            
            var positionStyles = '';
            if (position !== 'center') {
                overlay.style.alignItems = position.includes('top') ? 'flex-start' : position.includes('bottom') ? 'flex-end' : 'center';
                overlay.style.justifyContent = position.includes('left') ? 'flex-start' : position.includes('right') ? 'flex-end' : 'center';
                positionStyles = 'margin:2vw;';
            }
            
            var bgStyle = 'background:' + (config.background_color || '#fff') + ';';
            if (config.image_path && config.image_display_type === 'background') {
                bgStyle = 'background:url(' + config.image_path + ') center center / contain no-repeat, ' + (config.background_color || '#fff') + ';';
            } else if (config.image_path && config.image_display_type === 'background_cover') {
                bgStyle = 'background:url(' + config.image_path + ') center center / cover no-repeat, ' + (config.background_color || '#fff') + ';';
            }
            
            // Mobile-optimized popup styles - NO max-height initially, let content determine size
            var mobilePadding = isMobile ? 'padding:4vw;' : 'padding:2rem;';
            
            popup.style.cssText = bgStyle + 'border-radius:' + (config.border_radius || 12) + 'px;' + mobilePadding + 'width:92vw;' + sizeStyles[size] + positionStyles + (config.has_shadow ? 'box-shadow:0 4vw 12vw rgba(0,0,0,0.3);' : '') + 'position:relative;text-align:center;transform:scale(0.9);opacity:0;transition:all ' + (config.animation_duration || 300) + 'ms;direction:' + (isHe ? 'rtl' : 'ltr') + ';overflow-x:hidden;box-sizing:border-box;';
            
            // Close button with minimum 44x44px tap area for accessibility
            if (config.show_close_button) {
                var closeBtn = document.createElement('button');
                closeBtn.innerHTML = '&times;';
                closeBtn.style.cssText = 'position:absolute;top:2vw;' + (config.close_button_position === 'top-left' ? 'left' : 'right') + ':2vw;background:rgba(0,0,0,0.1);border:none;font-size:max(6vw, 24px);cursor:pointer;color:#666;line-height:1;padding:0;min-width:44px;min-height:44px;width:max(10vw, 44px);height:max(10vw, 44px);border-radius:50%;display:flex;align-items:center;justify-content:center;touch-action:manipulation;-webkit-tap-highlight-color:transparent;';
                closeBtn.setAttribute('aria-label', isHe ? 'סגור' : 'Close');
                closeBtn.onclick = function() { self.closePopup(overlay, config); };
                popup.appendChild(closeBtn);
            }
            
            // Image with responsive constraints - smaller on mobile to fit content
            if (config.image_path && (!config.image_display_type || config.image_display_type === 'inline')) {
                var img = document.createElement('img');
                img.src = config.image_path;
                var imgMaxHeight = isMobile ? 'max-height:min(150px, 20vh);' : 'max-height:40vh;';
                img.style.cssText = 'width:100%;max-width:100%;height:auto;' + imgMaxHeight + 'border-radius:2vw;margin-bottom:3vw;object-fit:contain;display:block;';
                popup.appendChild(img);
            }
            
            var title = isHe ? config.title_he : config.title_en;
            if (title) {
                var h2 = document.createElement('h2');
                h2.textContent = title;
                var titleBgStyle = '';
                if (config.title_bg_opacity && config.title_bg_opacity > 0) {
                    var titleBgColor = config.title_bg_color || '#000000';
                    var titleOpacity = (config.title_bg_opacity || 0) / 100;
                    titleBgStyle = 'background:' + self.hexToRgba(titleBgColor, titleOpacity) + ';padding:0.5rem 1rem;border-radius:4px;display:inline-block;';
                }
                h2.style.cssText = 'color:' + (config.title_color || '#1B2951') + ';font-size:' + (config.title_font_size || 24) + 'px;margin:0 0 1rem 0;font-weight:700;' + titleBgStyle;
                popup.appendChild(h2);
            }
            
            var content = isHe ? config.content_he : config.content_en;
            if (content) {
                var p = document.createElement('p');
                p.textContent = content;
                var textBgStyle = '';
                if (config.text_bg_opacity && config.text_bg_opacity > 0) {
                    var textBgColor = config.text_bg_color || '#000000';
                    var textOpacity = (config.text_bg_opacity || 0) / 100;
                    textBgStyle = 'background:' + self.hexToRgba(textBgColor, textOpacity) + ';padding:0.5rem 1rem;border-radius:4px;';
                }
                p.style.cssText = 'color:' + (config.text_color || '#333') + ';font-size:' + (config.content_font_size || 16) + 'px;margin:0 0 1.5rem 0;line-height:1.6;' + textBgStyle;
                popup.appendChild(p);
            }
            
            // Form or Button
            if (config.enable_form) {
                var form = this.createForm(config, isHe, overlay);
                popup.appendChild(form);
            } else {
                var btnText = isHe ? config.button_text_he : config.button_text_en;
                if (btnText) {
                    var btn = document.createElement('a');
                    btn.textContent = btnText;
                    btn.href = config.button_url || '#';
                    if (config.button_action === 'new_tab') btn.target = '_blank';
                    var btnBgOpacity = (config.button_bg_opacity !== undefined ? config.button_bg_opacity : 100) / 100;
                    var btnBgStyle = btnBgOpacity < 1 ? self.hexToRgba(config.button_bg_color || '#C75450', btnBgOpacity) : (config.button_bg_color || '#C75450');
                    btn.style.cssText = 'display:inline-block;background:' + btnBgStyle + ';color:' + (config.button_text_color || '#fff') + ';padding:0.875rem 2rem;border-radius:8px;text-decoration:none;font-weight:600;transition:transform 0.2s;';
                    btn.onmouseover = function() { this.style.transform = 'scale(1.05)'; };
                    btn.onmouseout = function() { this.style.transform = 'scale(1)'; };
                    if (config.button_action === 'close') {
                        btn.onclick = function(e) { e.preventDefault(); self.closePopup(overlay, config); };
                    } else {
                        btn.onclick = function() { self.trackClick(config.id, config); };
                    }
                    popup.appendChild(btn);
                }
            }
            
            overlay.appendChild(popup);
            document.body.appendChild(overlay);
            
            // Dynamic sizing using REAL visual viewport (accounts for mobile browser chrome)
            var adjustPopupSize = function() {
                // Use visualViewport API for real mobile devices (accounts for address bar, nav bar)
                var viewportHeight = window.visualViewport ? window.visualViewport.height : document.documentElement.clientHeight;
                var overlayPadding = isMobile ? viewportHeight * 0.02 : 20; // 2vw or 20px
                var maxAllowedHeight = viewportHeight - (overlayPadding * 2) - 20; // Leave 20px margin
                var popupHeight = popup.scrollHeight;
                
                if (popupHeight > maxAllowedHeight) {
                    // Content exceeds visible viewport - enable scrolling
                    popup.style.maxHeight = maxAllowedHeight + 'px';
                    popup.style.overflowY = 'auto';
                    popup.style.webkitOverflowScrolling = 'touch';
                } else {
                    // Content fits - no scroll needed
                    popup.style.maxHeight = '';
                    popup.style.overflowY = 'visible';
                }
            };
            
            requestAnimationFrame(function() {
                adjustPopupSize();
                overlay.style.opacity = '1';
                popup.style.transform = 'scale(1)';
                popup.style.opacity = '1';
            });
            
            // Re-adjust when mobile browser chrome expands/collapses
            if (window.visualViewport) {
                window.visualViewport.addEventListener('resize', adjustPopupSize);
            }
            
            if (config.allow_backdrop_close) {
                overlay.onclick = function(e) {
                    if (e.target === overlay) self.closePopup(overlay, config);
                };
            }
            
            this.markShown(config);
            this.trackImpression(config.id, config);
            
            if (config.auto_close_seconds) {
                setTimeout(function() {
                    self.closePopup(overlay, config);
                }, config.auto_close_seconds * 1000);
            }
        },
        
        closePopup: function(overlay, config) {
            var popup = overlay.querySelector('.site-popup');
            overlay.style.opacity = '0';
            if (popup) {
                popup.style.transform = 'scale(0.9)';
                popup.style.opacity = '0';
            }
            setTimeout(function() {
                if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
            }, config.animation_duration || 300);
            
            this.trackClose(config.id, config);
        },
        
        markShown: function(config) {
            this.shown[config.id] = Date.now();
            this.saveShownState();
            sessionStorage.setItem('popup_' + config.id, '1');
        },
        
        createForm: function(config, isHe, overlay) {
            var self = this;
            var form = document.createElement('form');
            form.style.cssText = 'margin-top:1rem;text-align:' + (isHe ? 'right' : 'left') + ';';
            
            var inputStyle = 'width:100%;padding:0.75rem 1rem;margin-bottom:0.75rem;border:1px solid #ddd;border-radius:8px;font-size:14px;box-sizing:border-box;direction:' + (isHe ? 'rtl' : 'ltr') + ';';
            
            // Name field
            if (config.collect_name) {
                var nameInput = document.createElement('input');
                nameInput.type = 'text';
                nameInput.name = 'name';
                nameInput.placeholder = isHe ? config.name_placeholder_he : config.name_placeholder_en;
                nameInput.required = config.name_required;
                nameInput.style.cssText = inputStyle;
                form.appendChild(nameInput);
            }
            
            // Email field
            if (config.collect_email) {
                var emailInput = document.createElement('input');
                emailInput.type = 'email';
                emailInput.name = 'email';
                emailInput.placeholder = isHe ? config.email_placeholder_he : config.email_placeholder_en;
                emailInput.required = config.email_required;
                emailInput.style.cssText = inputStyle;
                form.appendChild(emailInput);
            }
            
            // Phone field
            if (config.collect_phone) {
                var phoneInput = document.createElement('input');
                phoneInput.type = 'tel';
                phoneInput.name = 'phone';
                phoneInput.placeholder = isHe ? config.phone_placeholder_he : config.phone_placeholder_en;
                phoneInput.required = config.phone_required;
                phoneInput.style.cssText = inputStyle;
                form.appendChild(phoneInput);
            }
            
            var checkboxStyle = 'display:flex;align-items:flex-start;margin-bottom:0.5rem;gap:0.5rem;font-size:13px;color:#666;cursor:pointer;';
            var checkboxInputStyle = 'margin-top:2px;flex-shrink:0;';
            
            // Newsletter consent
            if (config.show_newsletter_consent) {
                var newsletterLabel = document.createElement('label');
                newsletterLabel.style.cssText = checkboxStyle;
                var newsletterCheck = document.createElement('input');
                newsletterCheck.type = 'checkbox';
                newsletterCheck.name = 'newsletter_consent';
                newsletterCheck.checked = config.newsletter_default_checked;
                newsletterCheck.style.cssText = checkboxInputStyle;
                var newsletterText = document.createElement('span');
                newsletterText.textContent = isHe ? config.newsletter_consent_text_he : config.newsletter_consent_text_en;
                newsletterLabel.appendChild(newsletterCheck);
                newsletterLabel.appendChild(newsletterText);
                form.appendChild(newsletterLabel);
            }
            
            // Terms consent
            if (config.show_terms_consent) {
                var termsLabel = document.createElement('label');
                termsLabel.style.cssText = checkboxStyle;
                var termsCheck = document.createElement('input');
                termsCheck.type = 'checkbox';
                termsCheck.name = 'terms_consent';
                termsCheck.required = config.terms_consent_required;
                termsCheck.style.cssText = checkboxInputStyle;
                var termsText = document.createElement('span');
                termsText.textContent = isHe ? config.terms_consent_text_he : config.terms_consent_text_en;
                termsLabel.appendChild(termsCheck);
                termsLabel.appendChild(termsText);
                form.appendChild(termsLabel);
            }
            
            // Marketing consent
            if (config.show_marketing_consent) {
                var marketingLabel = document.createElement('label');
                marketingLabel.style.cssText = checkboxStyle;
                var marketingCheck = document.createElement('input');
                marketingCheck.type = 'checkbox';
                marketingCheck.name = 'marketing_consent';
                marketingCheck.checked = config.marketing_default_checked;
                marketingCheck.style.cssText = checkboxInputStyle;
                var marketingText = document.createElement('span');
                marketingText.textContent = isHe ? config.marketing_consent_text_he : config.marketing_consent_text_en;
                marketingLabel.appendChild(marketingCheck);
                marketingLabel.appendChild(marketingText);
                form.appendChild(marketingLabel);
            }
            
            // Submit button
            var submitBtn = document.createElement('button');
            submitBtn.type = 'submit';
            submitBtn.textContent = isHe ? config.form_submit_text_he : config.form_submit_text_en;
            submitBtn.style.cssText = 'width:100%;margin-top:1rem;background:' + (config.button_bg_color || '#C75450') + ';color:' + (config.button_text_color || '#fff') + ';padding:0.875rem 2rem;border:none;border-radius:8px;font-size:16px;font-weight:600;cursor:pointer;transition:transform 0.2s;';
            submitBtn.onmouseover = function() { this.style.transform = 'scale(1.02)'; };
            submitBtn.onmouseout = function() { this.style.transform = 'scale(1)'; };
            form.appendChild(submitBtn);
            
            // Form submission handler
            form.onsubmit = function(e) {
                e.preventDefault();
                self.submitForm(form, config, overlay, isHe);
            };
            
            return form;
        },
        
        submitForm: function(form, config, overlay, isHe) {
            var self = this;
            var submitBtn = form.querySelector('button[type="submit"]');
            var originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = isHe ? 'שולח...' : 'Submitting...';
            
            var formData = {
                email: form.querySelector('input[name="email"]') ? form.querySelector('input[name="email"]').value : '',
                name: form.querySelector('input[name="name"]') ? form.querySelector('input[name="name"]').value : '',
                phone: form.querySelector('input[name="phone"]') ? form.querySelector('input[name="phone"]').value : '',
                newsletter_consent: form.querySelector('input[name="newsletter_consent"]') ? form.querySelector('input[name="newsletter_consent"]').checked : false,
                terms_consent: form.querySelector('input[name="terms_consent"]') ? form.querySelector('input[name="terms_consent"]').checked : false,
                marketing_consent: form.querySelector('input[name="marketing_consent"]') ? form.querySelector('input[name="marketing_consent"]').checked : false,
                source_page: window.location.href,
                screen_width: window.innerWidth,
                language: isHe ? 'he' : 'en',
                utm_source: self.getUrlParam('utm_source'),
                utm_medium: self.getUrlParam('utm_medium'),
                utm_campaign: self.getUrlParam('utm_campaign')
            };
            
            fetch('/api/popup/' + config.id + '/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    self.trackFormSubmit(config.id, config);
                    self.showFormSuccess(form, config, isHe, data.message, data.coupon_code, overlay);
                } else {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                    alert(data.error || (isHe ? 'אירעה שגיאה' : 'An error occurred'));
                }
            })
            .catch(function(error) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
                console.error('Form submission error:', error);
                alert(isHe ? 'אירעה שגיאה בשליחה' : 'Error submitting form');
            });
        },
        
        showFormSuccess: function(form, config, isHe, message, couponCode, overlay) {
            var self = this;
            form.innerHTML = '';
            
            var successDiv = document.createElement('div');
            successDiv.style.cssText = 'text-align:center;padding:1rem;';
            
            var checkmark = document.createElement('div');
            checkmark.innerHTML = '&#10003;';
            checkmark.style.cssText = 'font-size:48px;color:#28a745;margin-bottom:1rem;';
            successDiv.appendChild(checkmark);
            
            var successMsg = document.createElement('p');
            successMsg.textContent = message || (isHe ? 'תודה!' : 'Thank you!');
            successMsg.style.cssText = 'font-size:18px;color:#333;margin:0 0 1rem 0;';
            successDiv.appendChild(successMsg);
            
            if (couponCode) {
                var couponDiv = document.createElement('div');
                couponDiv.style.cssText = 'background:#f8f9fa;border:2px dashed #C75450;border-radius:8px;padding:1rem;margin:1rem 0;';
                var couponLabel = document.createElement('p');
                couponLabel.textContent = isHe ? 'קוד הקופון שלך:' : 'Your coupon code:';
                couponLabel.style.cssText = 'font-size:12px;color:#666;margin:0 0 0.5rem 0;';
                var couponCodeEl = document.createElement('p');
                couponCodeEl.textContent = couponCode;
                couponCodeEl.style.cssText = 'font-size:24px;font-weight:bold;color:#1B2951;margin:0;letter-spacing:2px;';
                couponDiv.appendChild(couponLabel);
                couponDiv.appendChild(couponCodeEl);
                successDiv.appendChild(couponDiv);
                
                var emailNote = document.createElement('p');
                emailNote.textContent = isHe ? 'הקופון נשלח גם לאימייל שלך' : 'Coupon also sent to your email';
                emailNote.style.cssText = 'font-size:12px;color:#888;margin:0.5rem 0 0 0;';
                successDiv.appendChild(emailNote);
            }
            
            form.appendChild(successDiv);
            
            setTimeout(function() {
                self.closePopup(overlay, config);
            }, 5000);
        },
        
        getUrlParam: function(name) {
            var url = new URL(window.location.href);
            return url.searchParams.get(name) || '';
        },
        
        trackImpression: function(popupId, config) {
            fetch('/api/popup/' + popupId + '/impression', { method: 'POST' }).catch(function(){});
            // Push to GTM
            var lang = document.documentElement.lang || 'he';
            this.pushGTMEvent('popup_impression', {
                'popup_id': popupId,
                'popup_title': config ? (lang === 'he' ? config.title_he : config.title_en) : '',
                'popup_type': config ? config.popup_type : '',
                'popup_position': config ? config.popup_position : ''
            });
        },
        
        trackClick: function(popupId, config) {
            fetch('/api/popup/' + popupId + '/click', { method: 'POST' }).catch(function(){});
            // Push to GTM
            var lang = document.documentElement.lang || 'he';
            this.pushGTMEvent('popup_cta_click', {
                'popup_id': popupId,
                'popup_title': config ? (lang === 'he' ? config.title_he : config.title_en) : '',
                'button_url': config ? config.button_url : ''
            });
        },
        
        trackClose: function(popupId, config) {
            fetch('/api/popup/' + popupId + '/close', { method: 'POST' }).catch(function(){});
            // Push to GTM
            var lang = document.documentElement.lang || 'he';
            this.pushGTMEvent('popup_close', {
                'popup_id': popupId,
                'popup_title': config ? (lang === 'he' ? config.title_he : config.title_en) : ''
            });
        },
        
        trackFormSubmit: function(popupId, config) {
            // Push to GTM
            var lang = document.documentElement.lang || 'he';
            this.pushGTMEvent('popup_form_submit', {
                'popup_id': popupId,
                'popup_title': config ? (lang === 'he' ? config.title_he : config.title_en) : ''
            });
        },
        
        hexToRgba: function(hex, opacity) {
            hex = hex.replace('#', '');
            if (hex.length === 3) {
                hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
            }
            var r = parseInt(hex.substring(0, 2), 16);
            var g = parseInt(hex.substring(2, 4), 16);
            var b = parseInt(hex.substring(4, 6), 16);
            return 'rgba(' + r + ',' + g + ',' + b + ',' + opacity + ')';
        }
    };
    
    window.SitePopup = SitePopup;
})();
