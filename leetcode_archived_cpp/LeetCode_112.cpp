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
    bool hasPathSum(TreeNode* root, int sum) {
        if (root == nullptr)
            return false;
        if (root->left == nullptr && root->right == nullptr && sum == root->val)
            return true;

        bool left = false, right = false;
        left = hasPathSum(root->left, sum-root->val);
        right = hasPathSum(root->right, sum-root->val);
        // cout << left << ' ' << right << ' ' << root->val << ' '<< sum << endl;
        return left || right;
    }
};

//少考虑了存在负数的情况，去掉一行边界条件就好了
