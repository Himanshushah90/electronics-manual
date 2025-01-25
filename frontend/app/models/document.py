from .. import mongo
from bson import ObjectId
from datetime import datetime

class Document:
    def __init__(self, data=None):
        self.data = data or {}
    
    @property
    def id(self):
        return str(self.data.get('_id'))
    
    @property
    def title(self):
        return self.data.get('title')
    
    @property
    def content(self):
        return self.data.get('content')
    
    @property
    def category_id(self):
        return str(self.data.get('category_id')) if self.data.get('category_id') else None
    
    @property
    def category(self):
        if self.category_id:
            from .category import Category
            return Category.find_by_id(self.category_id)
        return None

    @property
    def show_on_home(self):
        return self.data.get('show_on_home', False)
    
    @property
    def file(self):
        return self.data.get('file')
    
    @property 
    def file_url(self):
        return self.data.get('file', {}).get('filename') if self.data.get('file') else None
    
    @property
    def file_type(self):
        return self.data.get('file', {}).get('content_type') if self.data.get('file') else None
    
    @property
    def updated_at(self):
        return self.data.get('updated_at', datetime.utcnow())

    @classmethod
    def search(cls, query):
        """Search documents by title or content"""
        if not query:
            return []
        try:
            docs = mongo.db.documents.find({
                '$or': [
                    {'title': {'$regex': query, '$options': 'i'}},
                    {'content': {'$regex': query, '$options': 'i'}}
                ]
            }).sort('title', 1)
            return [cls(doc) for doc in docs]
        except:
            return []

    @classmethod
    def find_by_category(cls, category_id):
        if not category_id:
            return []
        try:
            docs = mongo.db.documents.find({'category_id': ObjectId(category_id)}).sort('title', 1)
            return [cls(doc) for doc in docs]
        except:
            return []
    
    @classmethod
    def get_featured(cls):
        return [cls(doc) for doc in mongo.db.documents.find({'show_on_home': True})]

    @classmethod
    def find_by_id(cls, id):
        try:
            data = mongo.db.documents.find_one({'_id': ObjectId(id)})
            return cls(data) if data else None
        except:
            return None