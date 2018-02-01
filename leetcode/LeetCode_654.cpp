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
    TreeNode* constructMaximumBinaryTree(vector<int>& nums) {
        stack<TreeNode*> stack_;
        for (int i = 0;i < nums.size(); i++)
        {
            TreeNode* temp = new TreeNode(nums[i]);
            while(!stack_.empty() && stack_.top()->val < nums[i])
            {
                temp->left = stack_.top();
                stack_.pop();
            }

            if (!stack_.empty())
                stack_.top()->right = temp;
            stack_.push(temp);
        }

        while (stack_.size() > 1)
            stack_.pop();
        return stack_.empty() ? nullptr :stack_.top();
    }
};
