# Mica4U GitHub Pages Site

This directory contains the GitHub Pages site for Mica4U.

## Overview

The site is built with:
- **HTML5** with semantic markup
- **Bootstrap 5** for responsive design
- **Custom CSS** for styling and animations
- **Vanilla JavaScript** for interactivity
- **GitHub Pages** for hosting

## Features

- 📱 **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- 🎨 **Modern UI**: Clean, professional design with gradients and animations
- 🚀 **Fast Loading**: Optimized assets and minimal dependencies
- ♿ **Accessible**: Semantic HTML and ARIA support
- 🔍 **SEO Optimized**: Proper meta tags and structured data

## Structure

```
docs/
├── index.html          # Main page
├── _config.yml         # GitHub Pages configuration
├── icon.ico           # Favicon
└── assets/
    ├── css/
    │   └── style.css   # Custom styles
    ├── js/
    │   └── main.js     # JavaScript functionality
    └── images/         # Screenshots and assets
```

## Local Development

To test the site locally:

1. Navigate to the docs directory:
   ```bash
   cd docs
   ```

2. Start a local server:
   ```bash
   python -m http.server 8080
   ```

3. Open http://localhost:8080 in your browser

## GitHub Pages Setup

1. Go to repository Settings > Pages
2. Set Source to "Deploy from a branch"
3. Select branch: `main` or your current branch
4. Set folder to `/docs`
5. Click Save

The site will be available at: `https://drkctrldev.github.io/Mica4U`

## Content Sections

- **Hero**: Project introduction with download links
- **Features**: Key capabilities and benefits
- **Installation**: Setup instructions and system requirements
- **Gallery**: Visual showcase of effects
- **Contribute**: Community guidelines and GitHub integration
- **Contact**: Maintainer information and support

## Customization

- Edit `index.html` for content changes
- Modify `assets/css/style.css` for styling
- Update `assets/js/main.js` for functionality
- Replace images in `assets/images/` as needed

## Performance

The site is optimized for performance:
- Minimal external dependencies (only Bootstrap CSS/JS from CDN)
- Optimized images
- Efficient CSS and JavaScript
- Semantic HTML structure