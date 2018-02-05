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
    vector<int> preorderTraversal(TreeNode* root) {
        vector<int> ans;
        preorder(ans, root);
        return ans;
    }

    void preorder(vector<int>& ans, TreeNode* root)
    {
        if (!root)
            return ;
        ans.push_back(root->val);
        preorder(ans, root->left);
        preorder(ans, root->right);
    }
};
