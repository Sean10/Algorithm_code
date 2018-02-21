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
    int rob(TreeNode* root) {
        vector<int> ans = dfs(root);
        return max(ans[0], ans[1]);
    }

    vector<int> dfs(TreeNode* root)
    {
        if (!root)
            return {0, 0};
        vector<int> left = dfs(root->left);
        vector<int> right = dfs(root->right);
        vector<int> ans{0, 0};
        ans[0] = left[1] + right[1] + root->val;
        ans[1] = max(left[0], left[1]) + max(right[0], right[1]);
        return ans;
    }
};
