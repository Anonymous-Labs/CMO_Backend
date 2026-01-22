# Import all the CRUD modules / instances
from . import user
from .business import CRUDBusiness
from app.models.business import Business

business = CRUDBusiness(Business)
