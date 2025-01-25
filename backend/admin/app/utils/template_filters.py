import re
import markdown
from flask import Markup
from datetime import datetime

def init_filters(app):
    @app.template_filter('markdown')
    def markdown_filter(text):
        if not text:
            return ''
        return Markup(markdown.markdown(text, extensions=['fenced_code', 'tables']))

    @app.template_filter('preview')
    def preview_filter(text, length=200):
        if not text:
            return ''
        text = re.sub(r'#.*?\n', '', text)  # Remove headers
        text = re.sub(r'\s+', ' ', text)    # Normalize whitespace
        if len(text) > length:
            text = text[:length] + '...'
        return text

    @app.template_filter('highlight')
    def highlight_filter(text, query):
        if not text or not query:
            return text
        pattern = re.compile(f'({re.escape(query)})', re.IGNORECASE)
        return Markup(pattern.sub(r'<span class="search-highlight">\1</span>', text))
    
    @app.template_filter('datetime')
    def datetime_filter(value):
        if not value:
            return ''
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return value
        return value.strftime('%B %d, %Y at %I:%M %p')
    
    @app.template_filter('file_icon')
    def file_icon_filter(filename):
        if not filename:
            return 'fas fa-file'
        ext = filename.split('.')[-1].lower()
        icons = {
            'pdf': 'fas fa-file-pdf',
            'doc': 'fas fa-file-word',
            'docx': 'fas fa-file-word',
            'xls': 'fas fa-file-excel',
            'xlsx': 'fas fa-file-excel',
            'txt': 'fas fa-file-alt',
            'md': 'fas fa-file-code',
            'jpg': 'fas fa-file-image',
            'jpeg': 'fas fa-file-image',
            'png': 'fas fa-file-image',
            'gif': 'fas fa-file-image'
        }
        return icons.get(ext, 'fas fa-file')

    @app.template_filter('breadcrumbs')
    def breadcrumbs_filter(category):
        if not category:
            return []
        breadcrumbs = []
        current = category
        while current:
            breadcrumbs.insert(0, current)
            current = current.parent
        return breadcrumbs