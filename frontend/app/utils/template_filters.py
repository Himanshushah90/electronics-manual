import re
import markdown
import os
from markupsafe import Markup
from datetime import datetime
from urllib.parse import urlparse
from flask import url_for

def init_filters(app):
    @app.template_filter('markdown')
    def markdown_filter(text):
        if not text:
            return ''
        
        try:

            

            if '![' not in text:
                return Markup(markdown.markdown(text, extensions=['fenced_code', 'tables']))
            
            class ImageUrlExtension(markdown.Extension):
                def extendMarkdown(self, md):
                    old_image_pattern = md.inlinePatterns['image']
                    
                    class NewImagePattern(old_image_pattern.__class__):
                        def handleMatch(self, m):
                            node = old_image_pattern.handleMatch(m)
                            if node is not None and node.get('src'):
                                src = node.get('src')
                                if not urlparse(src).netloc and not src.startswith('/'):
                                    node.set('src', url_for('main.serve_image', filename=os.path.basename(src)))
                            return node
                    
                    md.inlinePatterns['image'] = NewImagePattern(old_image_pattern.pattern, md)

            md = markdown.Markdown(extensions=['fenced_code', 'tables', ImageUrlExtension()])
            html = md.convert(text)
            return Markup(html)
        
        except Exception as e:
            print(f"Markdown conversion error: {e}")
            return Markup(text)

    @app.template_filter('preview')
    def preview_filter(text, length=200):
        if not text:
            return ''
        text = re.sub(r'#.*?\n', '', text)
        text = re.sub(r'\s+', ' ', text)
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