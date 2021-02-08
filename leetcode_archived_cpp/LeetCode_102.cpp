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
    vector<vector<int>> levelOrder(TreeNode* root) {
        queue<TreeNode*> q_;
        vector<vector<int>> ans;
        vector<int> temp;
        int size_parent = 1, size_child = 0;

        if(root)
        {
            q_.push(root);
        }
        else
            return ans;
        while(!q_.empty())
        {
            TreeNode* curr = q_.front();
            q_.pop();
            temp.push_back(curr->val);

            if(curr->left)
            {
                q_.push(curr->left);
                size_child ++;
            }
            if(curr->right)
            {
                q_.push(curr->right);
                size_child++;
            }

            size_parent--;
            if(size_parent == 0)
            {
                ans.push_back(temp);
                temp.clear();
                size_parent = size_child;
                size_child = 0;
            }
        }
        return ans;
    }
};
