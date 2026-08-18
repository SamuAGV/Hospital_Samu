# apps/users/utils.py
import hashlib
import base64

def hash_password(password):
    """
    Hashea una contraseña de manera consistente usando SHA256.
    """
    # Asegurar que la contraseña es string y codificarla en UTF-8
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
    
    # Crear hash SHA256
    hash_obj = hashlib.sha256(password_bytes)
    # Retornar en hexadecimal (formato consistente)
    return hash_obj.hexdigest()

def verify_password(password, hashed_password):
    """
    Verifica si una contraseña coincide con su hash.
    """
    return hash_password(password) == hashed_password