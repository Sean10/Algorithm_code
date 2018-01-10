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
    int getMinimumDifference(TreeNode* root) {
        int minn = INT_MAX, val = -1;
        helper(minn, val,root);
        return minn;
    }

    void helper(int& minn, int& val,TreeNode* root)
    {
        if(root == nullptr)
            return;
        if(root->left != nullptr)
            helper(minn, val, root->left);
        if(val >= 0)
            minn = min(minn, root->val - val);
        val = root->val;
        if(root->right != nullptr)
            helper(minn, val, root->right);
    }
};
