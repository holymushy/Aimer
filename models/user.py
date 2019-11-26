from app import db

from .base import create_uuid_string, UUID_LENGTH

class User(db.Model):
	__tablename__ = 'user'
