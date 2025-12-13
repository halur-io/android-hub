(function() {
    'use strict';
    
    var SitePopup = {
        config: null,
        shown: {},
        
        init: function(popupConfigs) {
            if (!popupConfigs || !popupConfigs.length) return;
            
            this.loadShownState();
            
            var self = this;
            popupConfigs.sort(function(a, b) { return b.priority - a.priority; });
            
            popupConfigs.forEach(function(config) {
                if (self.shouldShow(config)) {
                    self.schedulePopup(config);
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
            
            var overlay = document.createElement('div');
            overlay.className = 'site-popup-overlay';
            overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:' + (config.overlay_color || 'rgba(0,0,0,0.5)') + ';z-index:99999;display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity ' + (config.animation_duration || 300) + 'ms;';
            
            var popup = document.createElement('div');
            popup.className = 'site-popup';
            
            var position = config.popup_position || 'center';
            var size = config.popup_size || 'medium';
            var sizeStyles = {
                small: 'max-width:350px;',
                medium: 'max-width:500px;',
                large: 'max-width:700px;',
                fullscreen: 'width:100%;height:100%;max-width:none;border-radius:0;'
            };
            
            var positionStyles = '';
            if (position !== 'center') {
                overlay.style.alignItems = position.includes('top') ? 'flex-start' : position.includes('bottom') ? 'flex-end' : 'center';
                overlay.style.justifyContent = position.includes('left') ? 'flex-start' : position.includes('right') ? 'flex-end' : 'center';
                positionStyles = 'margin:1rem;';
            }
            
            var bgStyle = 'background:' + (config.background_color || '#fff') + ';';
            if (config.image_path && config.image_display_type === 'background') {
                bgStyle = 'background:url(' + config.image_path + ') center center / contain no-repeat, ' + (config.background_color || '#fff') + ';';
            } else if (config.image_path && config.image_display_type === 'background_cover') {
                bgStyle = 'background:url(' + config.image_path + ') center center / cover no-repeat, ' + (config.background_color || '#fff') + ';';
            }
            popup.style.cssText = bgStyle + 'border-radius:' + (config.border_radius || 12) + 'px;padding:2rem;width:90%;' + sizeStyles[size] + positionStyles + (config.has_shadow ? 'box-shadow:0 20px 60px rgba(0,0,0,0.3);' : '') + 'position:relative;text-align:center;transform:scale(0.9);opacity:0;transition:all ' + (config.animation_duration || 300) + 'ms;direction:' + (isHe ? 'rtl' : 'ltr') + ';';
            
            if (config.show_close_button) {
                var closeBtn = document.createElement('button');
                closeBtn.innerHTML = '&times;';
                closeBtn.style.cssText = 'position:absolute;top:10px;' + (config.close_button_position === 'top-left' ? 'left' : 'right') + ':10px;background:none;border:none;font-size:28px;cursor:pointer;color:#999;line-height:1;padding:0;width:30px;height:30px;';
                closeBtn.onclick = function() { self.closePopup(overlay, config); };
                popup.appendChild(closeBtn);
            }
            
            if (config.image_path && (!config.image_display_type || config.image_display_type === 'inline')) {
                var img = document.createElement('img');
                img.src = config.image_path;
                img.style.cssText = 'max-width:100%;height:auto;border-radius:8px;margin-bottom:1rem;';
                popup.appendChild(img);
            }
            
            var title = isHe ? config.title_he : config.title_en;
            if (title) {
                var h2 = document.createElement('h2');
                h2.textContent = title;
                h2.style.cssText = 'color:' + (config.title_color || '#1B2951') + ';font-size:' + (config.title_font_size || 24) + 'px;margin:0 0 1rem 0;font-weight:700;';
                popup.appendChild(h2);
            }
            
            var content = isHe ? config.content_he : config.content_en;
            if (content) {
                var p = document.createElement('p');
                p.textContent = content;
                p.style.cssText = 'color:' + (config.text_color || '#333') + ';font-size:' + (config.content_font_size || 16) + 'px;margin:0 0 1.5rem 0;line-height:1.6;';
                popup.appendChild(p);
            }
            
            var btnText = isHe ? config.button_text_he : config.button_text_en;
            if (btnText) {
                var btn = document.createElement('a');
                btn.textContent = btnText;
                btn.href = config.button_url || '#';
                if (config.button_action === 'new_tab') btn.target = '_blank';
                btn.style.cssText = 'display:inline-block;background:' + (config.button_bg_color || '#C75450') + ';color:' + (config.button_text_color || '#fff') + ';padding:0.875rem 2rem;border-radius:8px;text-decoration:none;font-weight:600;transition:transform 0.2s;';
                btn.onmouseover = function() { this.style.transform = 'scale(1.05)'; };
                btn.onmouseout = function() { this.style.transform = 'scale(1)'; };
                if (config.button_action === 'close') {
                    btn.onclick = function(e) { e.preventDefault(); self.closePopup(overlay, config); };
                } else {
                    btn.onclick = function() { self.trackClick(config.id); };
                }
                popup.appendChild(btn);
            }
            
            overlay.appendChild(popup);
            document.body.appendChild(overlay);
            
            requestAnimationFrame(function() {
                overlay.style.opacity = '1';
                popup.style.transform = 'scale(1)';
                popup.style.opacity = '1';
            });
            
            if (config.allow_backdrop_close) {
                overlay.onclick = function(e) {
                    if (e.target === overlay) self.closePopup(overlay, config);
                };
            }
            
            this.markShown(config);
            this.trackImpression(config.id);
            
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
            
            this.trackClose(config.id);
        },
        
        markShown: function(config) {
            this.shown[config.id] = Date.now();
            this.saveShownState();
            sessionStorage.setItem('popup_' + config.id, '1');
        },
        
        trackImpression: function(popupId) {
            fetch('/api/popup/' + popupId + '/impression', { method: 'POST' }).catch(function(){});
        },
        
        trackClick: function(popupId) {
            fetch('/api/popup/' + popupId + '/click', { method: 'POST' }).catch(function(){});
        },
        
        trackClose: function(popupId) {
            fetch('/api/popup/' + popupId + '/close', { method: 'POST' }).catch(function(){});
        }
    };
    
    window.SitePopup = SitePopup;
})();
