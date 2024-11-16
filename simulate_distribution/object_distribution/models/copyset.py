class Copyset:
    def __init__(self):
        self.nodes = []
    
    def add_node(self, node):
        self.nodes.append(node)
    
    def remove_node(self, node):
        self.nodes = [n for n in self.nodes if n.id != node.id]
    
    def size(self):
        return len(self.nodes)
    
    def is_same(self, other_copyset):
        self_ids = set(node.id for node in self.nodes)
        other_ids = set(node.id for node in other_copyset.nodes)
        return self_ids == other_ids

    def __repr__(self):
        return f"Copyset(nodes={[node.id for node in self.nodes]})" 