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
    int ans = INT_MAX, pre = -1;
    int minDiffInBST(TreeNode* root) {
        if (root->left)
            minDiffInBST(root->left);
        if (pre >= 0)
            ans = min(ans, root->val - pre);
        pre = root->val;
        if (root->right)
            minDiffInBST(root->right);

        return ans;
    }

};

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
    int minDiffInBST(TreeNode* root) {
        vector<int> q;
        int ans = INT_MAX;
        helper(root,q);
        for (int i = 1; i < q.size(); i++)
            ans = min(ans, q[i] - q[i-1]);

        return ans;
    }

    void helper(TreeNode* root, vector<int>& q)
    {
        if (!root)
            return ;
        helper(root->left,q);
        q.push_back(root->val);
        helper(root->right, q);
    }
};
