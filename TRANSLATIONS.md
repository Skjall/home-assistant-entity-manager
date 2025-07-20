# Translation Guide

This project uses [Crowdin](https://crowdin.com) for community translations.

## For Translators

1. Visit our Crowdin project: [TO BE CREATED]
2. Select your language
3. Translate the strings
4. Submit your translations

## For Developers

### Initial Setup

1. Create a free Crowdin account at https://crowdin.com
2. Create a new project (Free for open source)
3. Get your project ID and API token
4. Add the API token as a GitHub secret named `CROWDIN_TOKEN`
5. Update `crowdin.yml` with your project ID

### File Structure

```
translations/
├── en.json              # Addon configuration strings
└── ui/
    └── en.json          # UI strings
```

### Adding New Strings

1. Add new strings to the English (`en.json`) files
2. Push to main branch
3. GitHub Action will automatically upload to Crowdin
4. Translators can then translate the new strings
5. Translations will be downloaded via PR

### Using Translations in Code

#### For Addon Configuration
Home Assistant automatically uses `/translations/{language}.json` for addon configuration.

#### For UI Strings
We need to implement a translation loader in the web UI. Example:

```javascript
// Load translations based on HA language
const userLang = navigator.language || 'en';
const lang = userLang.split('-')[0];

// Load translation file
const translations = await fetch(`/translations/ui/${lang}.json`)
    .then(r => r.json())
    .catch(() => fetch('/translations/ui/en.json').then(r => r.json()));

// Use translations
document.querySelector('h1').textContent = translations.header.title;
```

### Supported Languages

Initially supporting:
- English (en)
- German (de)
- French (fr)
- Spanish (es)
- Italian (it)
- Dutch (nl)
- Polish (pl)
- Portuguese (pt)
- Russian (ru)
- Chinese Simplified (zh-CN)
- Japanese (ja)

More languages can be added on Crowdin as needed.