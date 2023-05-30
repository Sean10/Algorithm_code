# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def delNodes(self, root: Optional[TreeNode], to_delete: List[int]) -> List[TreeNode]:
        roots = set()
        # roots.add(root)
        self.dfs(root, True, to_delete, roots)
        return roots
        

    def dfs(self, node: Optional[TreeNode], new_root: bool, to_delete: List[int], roots: Set[TreeNode]):
        if not node:
            return None
        current_node_to_delete = node.val in to_delete
        node.left = self.dfs(node.left, node.val in to_delete, to_delete, roots)
        node.right = self.dfs(node.right, node.val in to_delete, to_delete, roots)
        if new_root and not current_node_to_delete:
            roots.add(node)
        if new_root and current_node_to_delete:
            return None
        if not new_root and current_node_to_delete:
            return None
        return node
                
