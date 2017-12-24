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
    int DFS(TreeNode* curr, int& len)
    {
        int l = curr->left ? DFS(curr->left, len) : 0;
        int r = curr->right ? DFS(curr->right, len) : 0;
        int resl = curr->left && curr->left->val == curr->val ? l+1 : 0;
        int resr = curr->right && curr->right->val == curr->val ? r+1 : 0;
        len = max(len, resl+resr);
        return max(resl, resr);
    }

    int longestUnivaluePath(TreeNode* root) {
        int len = 0;
        if(root)
            DFS(root, len);
        return len;

    }
};
