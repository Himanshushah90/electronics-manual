import os
from .. import mongo
from bson import ObjectId
from datetime import datetime
from flask import current_app, url_for
from werkzeug.utils import secure_filename

class Document:
    collection = mongo.db.documents
    
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
    def show_on_home(self):
        return self.data.get('show_on_home', False)
    
    @property
    def file(self):
        """Get file information from document data"""
        return self.data.get('file')
    
    @property
    def updated_at(self):
        return self.data.get('updated_at', datetime.utcnow())

    @property
    def content_with_image_paths(self):
        """Convert relative image paths to absolute URLs"""
        content = self.content
        if content:
            # Add logging to debug image paths
            print(f"Original content: {content}")
            
            # Replace relative image paths with absolute URLs
            uploads_url = url_for('static', filename='uploads/', _external=True)
            content = content.replace('![](uploads/', f'![]({uploads_url}')
            content = content.replace('src="uploads/', f'src="{uploads_url}')
            
            print(f"Modified content: {content}")
        return content

    def save(self):
        if '_id' in self.data:
            self.collection.update_one(
                {'_id': self.data['_id']},
                {'$set': self.data}
            )
        else:
            self.data['_id'] = self.collection.insert_one(self.data).inserted_id
        return self

    def delete(self):
        if '_id' in self.data:
            self.collection.delete_one({'_id': self.data['_id']})

    @classmethod
    def find_by_id(cls, id):
        try:
            data = cls.collection.find_one({'_id': ObjectId(id)})
            return cls(data) if data else None
        except:
            return None

    @classmethod
    def get_all(cls):
        return [cls(doc) for doc in cls.collection.find()]

    @classmethod
    def save_image(cls, image_file):
        """Save an uploaded image and return its URL path"""
        if image_file:
            try:
                # Create uploads directory if it doesn't exist
                uploads_dir = os.path.join(current_app.static_folder, 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                
                # Secure the filename and save the file
                filename = secure_filename(f"{str(ObjectId())}_{image_file.filename}")
                file_path = os.path.join(uploads_dir, filename)
                image_file.save(file_path)
                
                # Print debug information
                print(f"Image saved to: {file_path}")
                return f"uploads/{filename}"
            except Exception as e:
                print(f"Error saving image: {str(e)}")
                return None
        return None