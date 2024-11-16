import hashlib

def get_hash(key):
    """Generate a hash value for a given key"""
    return int(hashlib.md5(str(key).encode()).hexdigest(), 16)

def crush_hash(x, r):
    """CRUSH hash function"""
    h = hashlib.md5(f"{x}:{r}".encode()).hexdigest()
    return int(h, 16) 