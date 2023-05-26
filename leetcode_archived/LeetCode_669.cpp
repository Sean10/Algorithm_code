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
    TreeNode* trimBST(TreeNode* root, int L, int R) {
        return helper(root, L, R);
    }
    
    TreeNode* helper(TreeNode* root, int L, int R)
    {
        if (root->right != nullptr)
        {
            root->right = helper(root->right, L, R);
        }
        
        if (root->left != nullptr)
        {
            root->left = helper(root->left, L, R);
        }
        
        if (root->val > R)
            return root->left;
        if (root->val < L)
            return root->right;
        return root;
    }
};
