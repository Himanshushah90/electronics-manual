from .. import mongo
from bson import ObjectId

class Category:
    collection = mongo.db.categories
    
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
    def show_on_home(self):
        return self.data.get('show_on_home', False)
    
    @classmethod
    def get_all(cls):
        return [cls(cat) for cat in cls.collection.find()]
    
    @classmethod
    def find_by_id(cls, id):
        if not id:
            return None
        data = cls.collection.find_one({'_id': ObjectId(id)})
        return cls(data) if data else None
    
    def save(self):
        if not self.data.get('_id'):
            result = self.collection.insert_one(self.data)
            self.data['_id'] = result.inserted_id
        else:
            self.collection.update_one(
                {'_id': self.data['_id']},
                {'$set': self.data}
            )
        return self
    
    def delete(self):
        if self.data.get('_id'):
            self.collection.delete_one({'_id': self.data['_id']})
            return True
        return False