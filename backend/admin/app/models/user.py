from flask_login import UserMixin
from .. import mongo
from bson import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash

class User(UserMixin):
    def __init__(self, user_data):
        self.user_data = user_data
        
    def get_id(self):
        return str(self.user_data.get('_id'))
    
    @property
    def is_admin(self):
        return self.user_data.get('is_admin', False)
    
    def check_password(self, password):
        stored_hash = self.user_data.get('password', '')
        if not stored_hash.startswith('pbkdf2:sha256:'):
            # Update to new hash format
            new_hash = generate_password_hash(password)
            mongo.db.users.update_one(
                {'_id': self.user_data['_id']},
                {'$set': {'password': new_hash}}
            )
            return True
        return check_password_hash(stored_hash, password)
    
    @staticmethod
    def get(user_id):
        if not user_id:
            return None
        try:
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            return User(user_data) if user_data else None
        except:
            return None