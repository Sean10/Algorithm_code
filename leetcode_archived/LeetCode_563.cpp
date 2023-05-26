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
    int findTilt(TreeNode* root) {
        if(root == nullptr)
            return 0;
        int left = getSum(root->left);
        int right = getSum(root->right);
        //cout << left << right;
        return abs(left-right)+findTilt(root->left)+findTilt(root->right);
    }

    int getSum(TreeNode* root)
    {
        if(root == nullptr)
            return 0;
        return getSum(root->left)+root->val+getSum(root->right);
    }
};
