from .. import mongo
from bson import ObjectId

class Category:
    def __init__(self, data=None):
        self.data = data or {}
    
    @property
    def id(self):
        return str(self.data.get('_id'))
    
    @property
    def name(self):
        return self.data.get('name')
    
    @property
    def icon(self):
        return self.data.get('icon', 'fas fa-folder')
    
    @property
    def parent_id(self):
        return str(self.data.get('parent_id')) if self.data.get('parent_id') else None
    
    @property
    def parent(self):
        if self.parent_id:
            return self.find_by_id(self.parent_id)
        return None
    
    @property
    def documents(self):
        from .document import Document
        return Document.find_by_category(self.id)
    
    @property
    def subcategories(self):
        return [Category(cat) for cat in mongo.db.categories.find({'parent_id': ObjectId(self.id)})]
    
    @property
    def show_on_home(self):
        return self.data.get('show_on_home', False)

    @classmethod
    def get_all(cls):
        # Get root categories (those without parent)
        root_categories = [cls(cat) for cat in mongo.db.categories.find({'parent_id': None})]
        return root_categories
    
    @classmethod
    def get_featured(cls):
        # Fetch categories marked for home page display
        return [cls(cat) for cat in mongo.db.categories.find({'show_on_home': True})]
    
    @classmethod
    def find_by_id(cls, id):
        if not id:
            return None
        try:
            data = mongo.db.categories.find_one({'_id': ObjectId(id)})
            return cls(data) if data else None
        except:
            return None

    @classmethod
    def search(cls, query):
        """Search through categories and their subcategories"""
        try:
            # Search in all categories
            categories = [cls(cat) for cat in mongo.db.categories.find({
                'name': {'$regex': query, '$options': 'i'}
            })]
            
            # Get parent categories for any matching subcategories
            parent_ids = [cat.parent_id for cat in categories if cat.parent_id]
            if parent_ids:
                parent_categories = [cls(cat) for cat in mongo.db.categories.find({
                    '_id': {'$in': parent_ids}
                })]
                categories.extend(parent_categories)
            
            return list({cat.id: cat for cat in categories}.values())  # Remove duplicates
        except:
            return []