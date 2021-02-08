/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode(int x) : val(x), left(NULL), right(NULL) {}
 * };
 */
class Solution {
public:
    
    void helper(TreeNode* &root) {
        if (        {
            root = nullptr;
        }
        else {
            helper(root->left);
            helper(root->right);
        }
    }
    
    bool judge(TreeNode* root) {
        if (!root)
            return false;
        if (root->val == 1)
            return true;
        return judge(root->left) || judge(root->right);
    }
    
    TreeNode* pruneTree(TreeNode* root) {
        helper(root);
        return root;
    }
};
