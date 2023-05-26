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
    vector<string> binaryTreePaths(TreeNode* root) {
        vector<string> ans;

        if(root)
            helper(ans, root, to_string(root->val));

        return ans;
    }

    void helper(vector<string>& ans, TreeNode* root, string s)
    {
        if(root->left == nullptr && root->right == nullptr)
        {
            ans.push_back(s);
            return ;
        }

        if(root->left)
            helper(ans, root->left, s+"->"+to_string(root->left->val));
        if(root->right)
            helper(ans, root->right, s+"->"+to_string(root->right->val));
    }
};
