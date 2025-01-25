from flask import Blueprint, render_template, request, redirect, url_for
from ..models.category import Category
from ..models.document import Document
from bson import ObjectId

bp = Blueprint('views', __name__)

@bp.route('/')
def index():
    featured_categories = Category.get_featured()
    featured_documents = Document.get_featured()
    return render_template('home.html', 
                         featured_categories=featured_categories,
                         featured_documents=featured_documents)

@bp.route('/document/<id>')
def document(id):
    document = Document.find_by_id(id)
    if not document:
        return render_template('404.html'), 404
    return render_template('document.html', document=document)

@bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('views.index'))
        
    categories = Category.search(query)
    documents = Document.search(query)
    
    return render_template('search.html',
                         query=query,
                         categories=categories,
                         documents=documents)