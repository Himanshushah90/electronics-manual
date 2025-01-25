# admin/app/routes/categories.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from bson import ObjectId
from ..models.category import Category
from .. import db

bp = Blueprint('categories', __name__, url_prefix='/categories')

@bp.route('/')
@login_required
def index():
    categories = Category.get_all()  # Changed from find_all() to get_all()
    return render_template('categories/index.html', categories=categories)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        icon = request.form.get('icon')
        parent_id = request.form.get('parent_id')
        show_on_home = bool(request.form.get('show_on_home'))

        category = Category({
            'name': name,
            'icon': icon or 'fas fa-folder',
            'parent_id': ObjectId(parent_id) if parent_id else None,
            'show_on_home': show_on_home
        })
        
        try:
            category.save()
            flash('Category created successfully', 'success')
            return redirect(url_for('categories.index'))
        except Exception as e:
            flash(f'Error creating category: {str(e)}', 'error')

    parents = Category.get_all()
    return render_template('categories/create.html', categories=parents)

@bp.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    category = Category.find_by_id(id)
    if not category:
        flash('Category not found', 'error')
        return redirect(url_for('categories.index'))
    
    if request.method == 'POST':
        category.data.update({
            'name': request.form.get('name'),
            'icon': request.form.get('icon'),
            'parent_id': ObjectId(request.form.get('parent_id')) if request.form.get('parent_id') else None,
            'show_on_home': bool(request.form.get('show_on_home'))
        })
        try:
            category.save()
            flash('Category updated successfully', 'success')
            return redirect(url_for('categories.index'))
        except Exception as e:
            flash(f'Error updating category: {str(e)}', 'error')
    
    parents = Category.get_all()
    return render_template('categories/edit.html', category=category, parents=parents)

@bp.route('/delete/<id>', methods=['POST'])
@login_required
def delete(id):
    category = Category.find_by_id(id)
    if category:
        if category.delete():
            flash('Category deleted successfully', 'success')
        else:
            flash('Error deleting category', 'error')
    return redirect(url_for('categories.index'))