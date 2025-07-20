/**
 * Translation system for Entity Manager UI
 */
class TranslationManager {
    constructor() {
        this.translations = {};
        this.currentLang = 'en';
        this.fallbackLang = 'en';
    }

    /**
     * Initialize the translation system
     * Detects user language and loads translations
     */
    async init() {
        // Try to get language from Home Assistant
        const haLang = await this.getHALanguage();
        console.log('HA Language:', haLang);
        
        // Fallback to browser language
        const browserLang = navigator.language || navigator.userLanguage || 'en';
        console.log('Browser Language:', browserLang);
        
        // Use HA language if available, otherwise browser language
        const lang = haLang || browserLang.split('-')[0];
        console.log('Selected Language:', lang);
        
        // Load translations
        await this.loadLanguage(lang);
        
        return this;
    }

    /**
     * Try to get Home Assistant's configured language
     */
    async getHALanguage() {
        try {
            // This would need to be implemented based on how your addon can access HA config
            // For now, we'll check if there's a lang parameter in the URL or localStorage
            const urlParams = new URLSearchParams(window.location.search);
            const urlLang = urlParams.get('lang');
            if (urlLang) return urlLang;
            
            // Check localStorage
            const storedLang = localStorage.getItem('entityManagerLang');
            if (storedLang) return storedLang;
            
            return null;
        } catch (e) {
            console.error('Error getting HA language:', e);
            return null;
        }
    }

    /**
     * Load translations for a specific language
     */
    async loadLanguage(lang) {
        try {
            // Try to load the requested language
            console.log(`Loading language: ${lang}`);
            const url = `static/translations/${lang}.json`;
            console.log(`Fetching from: ${url}`);
            const response = await fetch(url);
            console.log(`Response status: ${response.status}`);
            if (response.ok) {
                this.translations = await response.json();
                this.currentLang = lang;
                localStorage.setItem('entityManagerLang', lang);
                console.log('Translations loaded:', this.translations);
            } else {
                console.log(`Failed to load ${lang}, falling back to English`);
                // Fallback to English
                await this.loadFallback();
            }
        } catch (error) {
            console.error(`Error loading language ${lang}:`, error);
            await this.loadFallback();
        }
    }

    /**
     * Load fallback language (English)
     */
    async loadFallback() {
        try {
            const response = await fetch(`static/translations/${this.fallbackLang}.json`);
            if (response.ok) {
                this.translations = await response.json();
                this.currentLang = this.fallbackLang;
            } else {
                console.error('Failed to load fallback language');
                this.translations = {};
            }
        } catch (error) {
            console.error('Error loading fallback language:', error);
            this.translations = {};
        }
    }

    /**
     * Get a translation by key path (e.g., "header.title")
     */
    t(key, params = {}) {
        const keys = key.split('.');
        let value = this.translations;
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                console.warn(`Translation key not found: ${key}`);
                return key; // Return the key if translation not found
            }
        }
        
        // Replace parameters like {count}
        if (typeof value === 'string') {
            return value.replace(/{(\w+)}/g, (match, param) => {
                return params[param] !== undefined ? params[param] : match;
            });
        }
        
        return value;
    }

    /**
     * Get current language
     */
    getCurrentLanguage() {
        return this.currentLang;
    }

    /**
     * Get available languages by checking which translation files exist
     */
    async getAvailableLanguages() {
        // This would need to be provided by the backend
        // For now, return the languages we know we have
        return [
            { code: 'en', name: 'English' },
            { code: 'de', name: 'Deutsch' }
        ];
    }

    /**
     * Switch to a different language
     */
    async switchLanguage(lang) {
        await this.loadLanguage(lang);
        // Trigger UI update
        window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
    }
}

// Create global instance
window.translations = new TranslationManager();