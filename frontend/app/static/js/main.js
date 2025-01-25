document.addEventListener('DOMContentLoaded', function() {
    // Create overlay element
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.appendChild(overlay);

    // Mobile menu toggle functionality
    function toggleMobileMenu() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.toggle('mobile-open');
            if (overlay) {
                overlay.classList.toggle('active');
            }
        }
    }

    // Add click event to all mobile menu toggle buttons
    const menuToggleButtons = document.querySelectorAll('.mobile-menu-toggle');
    menuToggleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleMobileMenu();
        });
    });

    // Category toggle functionality
    const categoryToggles = document.querySelectorAll('.category-toggle');
    categoryToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const content = this.closest('.nav-category').querySelector('.category-content');
            this.classList.toggle('expanded');
            if (content) {
                content.classList.toggle('expanded');
            }
        });
    });

    // Close sidebar when clicking overlay
    if (overlay) {
        overlay.addEventListener('click', function() {
            toggleMobileMenu();
        });
    }

    // Category toggles with improved hierarchy support
    function setupCategoryToggles() {
        document.querySelectorAll('.category-header').forEach(header => {
            header.addEventListener('click', function(e) {
                const toggle = this.querySelector('.category-toggle');
                if (!toggle) return;
                
                e.preventDefault();
                e.stopPropagation();
                
                const categoryContent = this.closest('.nav-category')
                                         .querySelector('.category-content');
                const isExpanded = categoryContent.classList.contains('expanded');
                
                // Toggle current category
                categoryContent.classList.toggle('expanded');
                toggle.style.transform = isExpanded ? 'rotate(0deg)' : 'rotate(90deg)';
            });
        });
    }

    // Initialize category toggles
    setupCategoryToggles();

    // Close sidebar when clicking outside
    document.addEventListener('click', function(e) {
        const sidebar = document.getElementById('sidebar');
        const menuToggle = document.querySelector('.mobile-menu-toggle');
        
        if (window.innerWidth <= 768 && 
            sidebar && 
            sidebar.classList.contains('mobile-open') && 
            !sidebar.contains(e.target) && 
            (!menuToggle || !menuToggle.contains(e.target))) {
            toggleMobileMenu();
        }
    });

    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('mobile-open');
            overlay.classList.remove('active');
        }
    });

    // Apply syntax highlighting to code blocks
    document.querySelectorAll('pre code').forEach((block) => {
        Prism.highlightElement(block);
    });

    // Handle search form submission
    const searchForm = document.querySelector('.search-wrapper form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const input = this.querySelector('input');
            if (!input.value.trim()) {
                e.preventDefault();
            }
        });
    }

    // Document content enhancement
    if (document.querySelector('.document-content')) {
        // Handle external links
        document.querySelectorAll('.document-content a').forEach(link => {
            if (link.hostname !== window.location.hostname) {
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
            }
        });

        // Add copy button to code blocks
        document.querySelectorAll('.document-content pre').forEach(block => {
            const button = document.createElement('button');
            button.className = 'copy-button';
            button.innerHTML = '<i class="fas fa-copy"></i>';
            
            button.addEventListener('click', async () => {
                const code = block.querySelector('code').textContent;
                try {
                    await navigator.clipboard.writeText(code);
                    button.innerHTML = '<i class="fas fa-check"></i>';
                    setTimeout(() => {
                        button.innerHTML = '<i class="fas fa-copy"></i>';
                    }, 2000);
                } catch (err) {
                    console.error('Failed to copy:', err);
                    button.innerHTML = '<i class="fas fa-times"></i>';
                }
            });
            
            block.appendChild(button);
        });
    }

    // Scroll to anchor links smoothly
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const target = document.getElementById(targetId);
            
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add active state to current document in sidebar
    const currentPath = window.location.pathname;
    const currentDocLink = document.querySelector(`.doc-item a[href="${currentPath}"]`);
    if (currentDocLink) {
        currentDocLink.classList.add('active');
        // Expand parent category
        const parentCategory = currentDocLink.closest('.category-content');
        if (parentCategory) {
            parentCategory.classList.add('expanded');
            const toggle = parentCategory.previousElementSibling
                                      .querySelector('.category-toggle');
            if (toggle) {
                toggle.style.transform = 'rotate(90deg)';
            }
        }
    }

    // Auto-expand current document's category
    if (currentDocLink) {
        let parent = currentDocLink.closest('.category-content');
        while (parent) {
            parent.classList.add('expanded');
            const toggle = parent.previousElementSibling
                               .querySelector('.category-toggle');
            if (toggle) {
                toggle.style.transform = 'rotate(90deg)';
            }
            parent = parent.closest('.nav-category')
                         .parentElement.closest('.category-content');
        }
    }

    // Real-time search with improvements
    const searchInput = document.getElementById('searchInput');
    const searchFormElement = document.getElementById('searchForm');
    const mainContent = document.querySelector('.content');
    let searchTimeout;
    let previousContent = '';

    searchInput.addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();

        if (query.length === 0) {
            // Restore previous content when search is cleared
            if (previousContent) {
                mainContent.innerHTML = previousContent;
            } else {
                window.location.href = '/';  // Redirect to home if no previous content
            }
            return;
        }

        searchTimeout = setTimeout(async () => {
            if (query.length >= 2) {
                try {
                    // Store current content before search
                    if (!previousContent) {
                        previousContent = mainContent.innerHTML;
                    }

                    const response = await fetch(`/search?q=${encodeURIComponent(query)}`, {
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });
                    
                    if (response.ok) {
                        const html = await response.text();
                        mainContent.innerHTML = html;
                    }
                } catch (error) {
                    console.error('Search error:', error);
                }
            }
        }, 300);
    });

    // Handle form submission
    searchFormElement.addEventListener('submit', function(e) {
        const query = searchInput.value.trim();
        if (!query) {
            e.preventDefault();
        }
    });

    // Back to Top functionality
    const backToTop = document.getElementById('backToTop');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    });

    backToTop.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Add image upload handling
    const imageUpload = document.getElementById('imageUpload');
    if (imageUpload) {
        imageUpload.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('image', file);

            try {
                const response = await fetch('/upload_image', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error('Upload failed');

                const data = await response.json();
                
                // Insert markdown at cursor position
                const textarea = document.querySelector('textarea[name="content"]');
                const cursorPos = textarea.selectionStart;
                const textBefore = textarea.value.substring(0, cursorPos);
                const textAfter = textarea.value.substring(cursorPos);
                
                textarea.value = textBefore + data.markdown + textAfter;
                
                // Update preview if exists
                const preview = document.getElementById('preview');
                if (preview) {
                    preview.innerHTML = marked.parse(textarea.value);
                }
            } catch (error) {
                console.error('Upload error:', error);
                alert('Failed to upload image');
            }
        });
    }

    let isSidebarOpen = false;

    const toggleSidebar = () => {
        isSidebarOpen = !isSidebarOpen;
    };
});