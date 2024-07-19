# __init__.py

from .connection import setup_milvus_connection
from .getEngineDetails import getEngineDetails
from .getInstanceDetails import get_instance_id

__all__ = [
    'setup_milvus_connection', 
    'getEngineDetails', 
    'get_instance_id'
]
