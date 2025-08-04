// Custom JavaScript for Mica4U GitHub Pages Site

document.addEventListener('DOMContentLoaded', function() {
    
    // Smooth scrolling for navigation links
    initSmoothScrolling();
    
    // Navbar scroll effect
    initNavbarScrollEffect();
    
    // Animate elements on scroll
    initScrollAnimations();
    
    // Initialize gallery functionality
    initGalleryFunctionality();
    
    // Initialize copy code functionality
    initCodeCopyFunctionality();
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize lazy loading for images
    initLazyLoading();
    
    console.log('Mica4U site initialized successfully!');
});

/**
 * Initialize smooth scrolling for navigation links
 */
function initSmoothScrolling() {
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 70; // Account for fixed navbar
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
                
                // Close mobile navbar if open
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse.classList.contains('show')) {
                    const navbarToggler = document.querySelector('.navbar-toggler');
                    navbarToggler.click();
                }
                
                // Update active nav link
                updateActiveNavLink(targetId);
            }
        });
    });
}

/**
 * Update active navigation link
 */
function updateActiveNavLink(targetId) {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === targetId) {
            link.classList.add('active');
        }
    });
}

/**
 * Initialize navbar scroll effect
 */
function initNavbarScrollEffect() {
    const navbar = document.querySelector('.navbar');
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Add/remove background opacity based on scroll position
        if (scrollTop > 50) {
            navbar.style.background = 'rgba(52, 58, 64, 0.98)';
            navbar.style.backdropFilter = 'blur(15px)';
        } else {
            navbar.style.background = 'rgba(52, 58, 64, 0.95)';
            navbar.style.backdropFilter = 'blur(10px)';
        }
        
        // Hide/show navbar on scroll (optional feature)
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down
            navbar.style.transform = 'translateY(-100%)';
        } else {
            // Scrolling up
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
        
        // Update active section based on scroll position
        updateActiveSection();
    });
}

/**
 * Update active section based on scroll position
 */
function updateActiveSection() {
    const sections = document.querySelectorAll('section[id]');
    const scrollPos = window.pageYOffset + 100;
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        const sectionId = '#' + section.getAttribute('id');
        
        if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
            updateActiveNavLink(sectionId);
        }
    });
}

/**
 * Initialize scroll animations
 */
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-on-scroll');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements to animate
    const elementsToAnimate = document.querySelectorAll('.feature-card, .contribution-card, .contact-card, .gallery-item, .card');
    elementsToAnimate.forEach(element => {
        observer.observe(element);
    });
}

/**
 * Initialize gallery functionality
 */
function initGalleryFunctionality() {
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    galleryItems.forEach(item => {
        const img = item.querySelector('img');
        
        // Add click event to show larger image
        item.addEventListener('click', function() {
            showImageModal(img.src, img.alt);
        });
        
        // Add keyboard navigation
        item.setAttribute('tabindex', '0');
        item.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                showImageModal(img.src, img.alt);
            }
        });
    });
}

/**
 * Show image in modal
 */
function showImageModal(imageSrc, imageAlt) {
    // Create modal if it doesn't exist
    let imageModal = document.getElementById('imageModal');
    
    if (!imageModal) {
        const modalHTML = `
            <div class="modal fade" id="imageModal" tabindex="-1">
                <div class="modal-dialog modal-xl modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Screenshot</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body text-center">
                            <img id="modalImage" src="" alt="" class="img-fluid">
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        imageModal = document.getElementById('imageModal');
    }
    
    // Update modal content
    const modalImage = document.getElementById('modalImage');
    const modalTitle = imageModal.querySelector('.modal-title');
    
    modalImage.src = imageSrc;
    modalImage.alt = imageAlt;
    modalTitle.textContent = imageAlt;
    
    // Show modal
    const modal = new bootstrap.Modal(imageModal);
    modal.show();
}

/**
 * Initialize code copy functionality
 */
function initCodeCopyFunctionality() {
    const codeBlocks = document.querySelectorAll('.code-block');
    
    codeBlocks.forEach(block => {
        // Add copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'btn btn-sm btn-outline-secondary copy-btn';
        copyButton.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
        copyButton.style.position = 'absolute';
        copyButton.style.top = '10px';
        copyButton.style.right = '10px';
        
        // Make code block relative positioned
        block.style.position = 'relative';
        block.appendChild(copyButton);
        
        // Add copy functionality
        copyButton.addEventListener('click', function() {
            const code = block.querySelector('code');
            if (code) {
                navigator.clipboard.writeText(code.textContent).then(() => {
                    // Show success feedback
                    const originalHTML = copyButton.innerHTML;
                    copyButton.innerHTML = '<i class="bi bi-check"></i> Copied!';
                    copyButton.classList.remove('btn-outline-secondary');
                    copyButton.classList.add('btn-success');
                    
                    setTimeout(() => {
                        copyButton.innerHTML = originalHTML;
                        copyButton.classList.remove('btn-success');
                        copyButton.classList.add('btn-outline-secondary');
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy code: ', err);
                });
            }
        });
    });
}

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipElements.forEach(element => {
        new bootstrap.Tooltip(element);
    });
}

/**
 * Initialize lazy loading for images
 */
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

/**
 * Utility function to debounce function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Add parallax effect to hero section (optional enhancement)
 */
function initParallaxEffect() {
    const heroSection = document.querySelector('.hero-section');
    
    if (heroSection) {
        window.addEventListener('scroll', debounce(() => {
            const scrolled = window.pageYOffset;
            const parallax = heroSection.querySelector('.hero-content');
            const speed = 0.5;
            
            if (parallax) {
                parallax.style.transform = `translateY(${scrolled * speed}px)`;
            }
        }, 10));
    }
}

/**
 * Initialize theme toggle (future enhancement)
 */
function initThemeToggle() {
    // Future enhancement: Add dark/light theme toggle
    // This would be useful for users who prefer different themes
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

/**
 * Track user interactions for analytics (optional)
 */
function initAnalytics() {
    // Track button clicks
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.textContent.trim();
            console.log(`Button clicked: ${action}`);
            // Here you could send data to analytics service
        });
    });
    
    // Track external link clicks
    const externalLinks = document.querySelectorAll('a[target="_blank"]');
    externalLinks.forEach(link => {
        link.addEventListener('click', function() {
            const url = this.href;
            console.log(`External link clicked: ${url}`);
            // Here you could send data to analytics service
        });
    });
}

/**
 * Initialize keyboard navigation
 */
function initKeyboardNavigation() {
    document.addEventListener('keydown', function(e) {
        // Press 'h' to go to home
        if (e.key === 'h' && !e.ctrlKey && !e.altKey) {
            const homeSection = document.querySelector('#home');
            if (homeSection) {
                homeSection.scrollIntoView({ behavior: 'smooth' });
            }
        }
        
        // Press 'g' to go to gallery
        if (e.key === 'g' && !e.ctrlKey && !e.altKey) {
            const gallerySection = document.querySelector('#gallery');
            if (gallerySection) {
                gallerySection.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
}

/**
 * Handle page visibility changes
 */
function initVisibilityHandler() {
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            console.log('Page is now hidden');
        } else {
            console.log('Page is now visible');
        }
    });
}

// Initialize optional enhancements
// Uncomment these if you want additional features
// initParallaxEffect();
// initThemeToggle();
// initAnalytics();
// initKeyboardNavigation();
// initVisibilityHandler();