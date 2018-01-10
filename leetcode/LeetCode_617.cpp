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
    TreeNode* mergeTrees(TreeNode* t1, TreeNode* t2) {
        TreeNode *root = nullptr;
        merge(root, t1, t2);
        return root;
    }

    void merge(TreeNode* &root, TreeNode* t1, TreeNode* t2)
    {
        if(!t1 && !t2)
            return ;
        int val_t1 = t1 ? t1->val : 0;
        int val_t2 = t2 ? t2->val : 0;
        root = new TreeNode(val_t1 + val_t2);
        TreeNode *t1_left = t1 ? t1->left : nullptr;
        TreeNode *t1_right = t1 ? t1->right : nullptr;
        TreeNode *t2_left = t2 ? t2->left : nullptr;
        TreeNode *t2_right = t2 ? t2->right : nullptr;
        merge(root->left, t1_left, t2_left);
        merge(root->right, t1_right, t2_right);
    }
};
