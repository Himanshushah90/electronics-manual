from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_required
from ..models.document import Document
from ..models.category import Category
from .. import mongo
from bson import ObjectId
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import mammoth
from bs4 import BeautifulSoup
import docx2md
import base64

bp = Blueprint('documents', __name__, url_prefix='/documents')

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'docx', 'doc'}

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

@bp.route('/')
@login_required
def index():
    # Changed from query.all() to use MongoDB's find()
    documents = Document.get_all()
    return render_template('documents/index.html', documents=documents)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            content = request.form.get('content')
            category_id = request.form.get('category_id')
            show_on_home = request.form.get('show_on_home') == 'on'  # Convert checkbox to boolean

            if not all([title, content, category_id]):
                flash('All fields are required', 'error')
                return redirect(url_for('documents.create'))

            # Handle file upload
            uploaded_file = None
            if 'document' in request.files:
                file = request.files['document']
                if file and file.filename and allowed_file(file.filename):
                    # Create uploads directory if it doesn't exist
                    uploads_dir = os.path.join(current_app.root_path, 'uploads')
                    os.makedirs(uploads_dir, exist_ok=True)
                    
                    # Generate unique filename
                    filename = secure_filename(f"{str(ObjectId())}_{file.filename}")
                    file_path = os.path.join(uploads_dir, filename)
                    
                    # Save the file
                    file.save(file_path)
                    print(f"File saved to: {file_path}")  # Debug print
                    
                    # Convert Word document to Markdown if it's a docx file
                    if file.filename.endswith('.docx'):
                        try:
                            content = docx2md(file_path)
                            
                            # Clean up the markdown
                            content = content.replace('\n\n\n', '\n\n')
                        except Exception as e:
                            print(f"Error converting document: {str(e)}")

                    uploaded_file = {
                        'filename': filename,
                        'original_name': file.filename,
                        'content_type': file.content_type
                    }

            document = Document({
                'title': title,
                'content': content,
                'category_id': ObjectId(category_id),
                'show_on_home': show_on_home,
                'file': uploaded_file if uploaded_file else None,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })

            document.save()
            flash('Document created successfully', 'success')
            return redirect(url_for('documents.index'))
        except Exception as e:
            flash(f'Error creating document: {str(e)}', 'error')
            print(f"Error: {str(e)}")  # Debug print

    categories = Category.get_all()
    return render_template('documents/create.html', categories=categories)

@bp.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    document = Document.find_by_id(id)
    if not document:
        flash('Document not found', 'error')
        return redirect(url_for('documents.index'))
    
    if request.method == 'POST':
        try:
            # Basic document data
            document.data.update({
                'title': request.form.get('title'),
                'category_id': ObjectId(request.form.get('category_id')),
                'show_on_home': bool(request.form.get('show_on_home'))
            })

            # Handle new content or file upload
            if 'document' in request.files and request.files['document'].filename:
                file = request.files['document']
                if file and allowed_file(file.filename):
                    # Delete old file if exists
                    if document.file:
                        old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.file['filename'])
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    
                    # Save ne file
                    filename = secure_filename(f"{str(ObjectId())}_{file.filename}")
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    # Convert Word document to HTML
                    if file.filename.endswith('.docx'):
                        with open(file_path, 'rb') as docx_file:
                            result = mammoth.convert_to_html(docx_file)
                            document.data['content'] = result.value
                    
                    document.data['file'] = {
                        'filename': filename,
                        'original_name': file.filename,
                        'content_type': file.content_type
                    }
            elif request.form.get('content'):  # If markdown content is provided
                document.data['content'] = request.form.get('content')
                # Remove file if switching to markdown
                if document.file:
                    old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.file['filename'])
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                    document.data['file'] = None

            document.save()
            flash('Document updated successfully', 'success')
            return redirect(url_for('documents.index'))
            
        except Exception as e:
            flash(f'Error updating document: {str(e)}', 'error')

    categories = Category.get_all()
    return render_template('documents/edit.html', document=document, categories=categories)

@bp.route('/delete/<id>', methods=['POST'])
@login_required
def delete(id):
    try:
        document = Document.find_by_id(id)
        if document:
            # Delete associated file if exists
            if document.file:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.file['filename'])
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Delete document from database
            document.delete()
            flash('Document deleted successfully', 'success')
        return redirect(url_for('documents.index'))
    except Exception as e:
        flash(f'Error deleting document: {str(e)}', 'error')
        return redirect(url_for('documents.index'))

@bp.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
        
    if file and allowed_image_file(file.filename):
        try:
            # Save image using Document model method
            image_path = Document.save_image(file)
            if image_path:
                # Return URLs for the image
                image_url = url_for('static', filename=image_path, _external=True)
                return jsonify({
                    'url': image_url,
                    'markdown': f'<img title="{file.filename}" alt="{file.filename}" src="{image_url}">'
                })
            return jsonify({'error': 'Failed to save image'}), 500
        except Exception as e:
            current_app.logger.error(f"Upload error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400