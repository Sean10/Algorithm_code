


/**
 * 这个版本只能计算出经过根节点的最大长度，感觉是需要一个标记的，标记这段返回长度是否连着的
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
    int longestUnivaluePath(TreeNode* root) {
        if(root == NULL)
            return 0;
        int len_left = longestUnivaluePath(root->left);
        int len_right = longestUnivaluePath(root->right);
        if((root->left && root->val == root->left->val) && (root->right && root->val == root->right->val))
        {
            len_left += 2;
            len_right += 2;
        }
        else if(root->right && root->val == root->right->val)
            len_right += 1;
        else if(root->left && root->val == root->left->val)
            len_left += 1;
        else
            return 0;//这里不对，这样就只能统计经过根节点的最大长度了
        return max(len_left, len_right);


    }
};
