from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, current_app
from ..models.category import Category
from ..models.document import Document
from bson import ObjectId
import mammoth
from werkzeug.utils import secure_filename
import os
from bs4 import BeautifulSoup
import docx2md
import base64
import re
from urllib.parse import urlparse

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    try:
        categories = Category.get_all()
        featured_categories = Category.get_featured()
        featured_documents = Document.get_featured()
        
        return render_template('home.html',
                             categories=categories,
                             featured_categories=featured_categories,
                             featured_documents=featured_documents)
    except Exception as e:
        print("Error in index route:", str(e))
        return render_template('home.html', 
                             categories=[],
                             featured_categories=[],
                             featured_documents=[])

@bp.route('/document/<id>')
def document(id):
    try:
        document = Document.find_by_id(id)
        categories = Category.get_all()
        
        if document and document.file:
            try:
                admin_upload_path = os.path.join(
                    current_app.root_path, 
                    '..', '..',
                    'backend', 
                    'admin',
                    'app', 
                    'uploads',
                    document.file['filename']
                )
                
                if os.path.exists(admin_upload_path):
                    style_map = """
                        p[style-name='Code'] => pre > code:fresh
                        p[style-name='Source Code'] => pre > code:fresh
                        p[style-name='Program'] => pre > code:fresh
                        p[style-name='MATLAB Code'] => pre > code.language-matlab:fresh
                        p[style-name='Python Code'] => pre > code.language-python:fresh
                        r[style-name='Code Char'] => code:fresh
                        p[style-name='Normal'] => p:fresh
                        p[style-name='Title'] => h1.title:fresh
                        p[style-name='Heading 1'] => h1:fresh
                        p[style-name='Heading 2'] => h2:fresh
                        p[style-name='Heading 3'] => h3:fresh
                        r[style-name='Strong'] => strong
                        r[style-name='Emphasis'] => em
                    """

                    with open(admin_upload_path, 'rb') as docx_file:
                        result = mammoth.convert_to_html(
                            docx_file,
                            style_map=style_map
                        )
                        
                        html = result.value
                        
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        for pre in soup.find_all('pre'):
                            code = pre.find('code')
                            if code:
                                language = 'language-python'
                                
                                code_text = str(code).lower()
                                if any(keyword in code_text for keyword in ['end;', 'function', '.m', 'matlab']):
                                    language = 'language-matlab'
                                elif 'python' in code_text or any(keyword in code_text for keyword in ['def ', 'import ', 'class ']):
                                    language = 'language-python'
                                
                                code['class'] = code.get('class', []) + [language]
                                pre['class'] = pre.get('class', []) + ['line-numbers']
                        
                        # Update the content in the original data dictionary
                        document.data['content'] = str(soup)

            except Exception as e:
                print(f"Error converting document: {str(e)}")
        
        # Modify image paths only if content exists
        if document and document.content:
            document.data['content'] = re.sub(
                r'!\[([^\]]*)\]\(([^)]+)\)', 
                lambda m: f'![{m.group(1)}]({url_for("main.serve_image", filename=os.path.basename(m.group(2)))})' 
                if not urlparse(m.group(2)).netloc and not m.group(2).startswith('/') 
                else m.group(0), 
                document.content
            )
        
        if document:
            return render_template('document.html', 
                                document=document,
                                categories=categories)
        return render_template('404.html', categories=categories), 404
        
    except Exception as e:
        print(f"Error in document route: {str(e)}")
        return render_template('404.html', categories=Category.get_all()), 404

@bp.route('/category/<id>')
def category(id):
    category = Category.find_by_id(id)
    if not category:
        return render_template('404.html', categories=Category.get_all()), 404
    
    categories = Category.get_all()
    
    return render_template('category.html',
                         category=category,
                         categories=categories)

@bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('main.index'))
        
    categories = Category.get_all()
    
    search_categories = [cat for cat in categories if query.lower() in cat.name.lower()]
    search_documents = Document.search(query)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('search_results.html',
                            query=query,
                            categories=categories,
                            search_categories=search_categories,
                            search_documents=search_documents)
    
    return render_template('search.html',
                         query=query,
                         categories=categories,
                         search_categories=search_categories,
                         search_documents=search_documents)

@bp.route('/static/uploads/<path:filename>')
def serve_image(filename):
    try:
        upload_directory = os.path.join(current_app.root_path, '..', '..', 
            'backend', 'admin', 'app', 'uploads')
        return send_from_directory(upload_directory, filename)
    except Exception as e:
        print(f"Error serving image: {str(e)}")
        return '', 404

@bp.route('/upload', methods=['POST'])
def upload_document():
    if 'document' not in request.files:
        return {'error': 'No file uploaded'}, 400
        
    file = request.files['document']
    if file.filename == '':
        return {'error': 'No file selected'}, 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        with open(file_path, 'rb') as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value
            
        content = html_to_markdown(html)
        
        return {'content': content}, 200
    
    return {'error': 'Invalid file type'}, 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'docx', 'doc'}

def html_to_markdown(html):
    """
    Convert HTML to markdown with improved image and formatting handling.
    
    Args:
        html (str): HTML content from Mammoth conversion
    
    Returns:
        str: Converted markdown with preserved images and formatting
    """
    # Use BeautifulSoup for more robust HTML parsing
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Handle images with proper markdown syntax
    for img in soup.find_all('img'):
        src = img.get('src', '')
        alt = img.get('alt', '')
        
        # Check if the image source is a local file
        if not urlparse(src).netloc and not src.startswith('/'):
            # Construct the correct URL for the local image
            src = url_for('main.serve_image', filename=os.path.basename(src))
        
        img.replace_with(f'![{alt}]({src})')
    
    # Convert headings
    for h1 in soup.find_all('h1'):
        h1.string = f'# {h1.text}'
    
    for h2 in soup.find_all('h2'):
        h2.string = f'## {h2.text}'
    
    for h3 in soup.find_all('h3'):
        h3.string = f'### {h3.text}'
    
    # Handle bold and italic
    for strong in soup.find_all('strong'):
        strong.string = f'**{strong.text}**'
    
    for em in soup.find_all('em'):
        em.string = f'*{em.text}*'
    
    # Convert code blocks
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        if code:
            language = code.get('class', [''])[0].replace('language-', '') if code.get('class') else ''
            pre.string = f'```{language}\n{code.text}\n```'
    
    # Convert paragraphs
    for p in soup.find_all('p'):
        p.string = p.text + '\n\n'
    
    # Remove any remaining HTML tags
    markdown_text = re.sub(r'<[^>]+>', '', str(soup))
    
    # Clean up excessive whitespace
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
    
    return markdown_text.strip()