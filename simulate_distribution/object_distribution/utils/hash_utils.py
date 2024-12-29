import hashlib

def get_hash(key):
    """Generate a hash value for a given key"""
    return int(hashlib.md5(str(key).encode()).hexdigest(), 16)

def crush_hash(x, r):
    """CRUSH hash function"""
    h = hashlib.md5(f"{x}:{r}".encode()).hexdigest()
    return int(h, 16) 

def rjenkins_hash(key):
    """
    Robert Jenkins' 32 bit hash function
    """
    # 将输入转换为字节
    if isinstance(key, str):
        key = key.encode()
    elif not isinstance(key, bytes):
        key = str(key).encode()
    
    hash = 0
    for byte in key:
        hash += byte
        hash += hash << 10
        hash ^= hash >> 6
    hash += hash << 3
    hash ^= hash >> 11
    hash += hash << 15
    return hash & 0xFFFFFFFF  # 确保结果是32位 