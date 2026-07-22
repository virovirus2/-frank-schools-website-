from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import json
import base64

class EncryptionService:
    """Handle encryption and decryption of votes"""
    
    def __init__(self):
        # In production, load keys from secure storage
        self.cipher_suite = Fernet(self._get_encryption_key())
        self.private_key = self._get_private_key()
        self.public_key = self._get_public_key()
    
    def _get_encryption_key(self):
        """Get or generate encryption key"""
        # In production, retrieve from environment or secure key management service
        return b'your-secret-key-base64-encoded-32-bytes-minimum'
    
    def _get_private_key(self):
        """Get RSA private key"""
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
    
    def _get_public_key(self):
        """Get RSA public key"""
        return self.private_key.public_key()
    
    def encrypt(self, data):
        """Encrypt vote data"""
        json_data = json.dumps(data).encode()
        encrypted = self.cipher_suite.encrypt(json_data)
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data):
        """Decrypt vote data"""
        decoded = base64.b64decode(encrypted_data.encode())
        decrypted = self.cipher_suite.decrypt(decoded)
        return json.loads(decrypted.decode())
    
    def sign(self, data):
        """Sign encrypted data with digital signature"""
        signature = self.private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()
    
    def verify(self, data, signature):
        """Verify digital signature"""
        try:
            self.public_key.verify(
                base64.b64decode(signature.encode()),
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False
