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
    int sumNumbers(TreeNode* root) {
        int sum = 0;
        sumAll(root,0,sum);
        return sum;
    }

    void sumAll(TreeNode* root, int temp_sum, int& sum)
    {
        if(!root)
            return ;
        temp_sum = temp_sum*10 + root->val;
        if(!root->left && !root->right)
        {
            sum += temp_sum;
            return ;
        }
        sumAll(root->left, temp_sum, sum);
        sumAll(root->right, temp_sum, sum);

    }
};
