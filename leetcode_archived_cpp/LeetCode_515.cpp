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
    vector<int> largestValues(TreeNode* root) {
        queue<pair<TreeNode*, int>> q;
        if(root)
            q.push(make_pair(root, 1));
        vector<int> left;
        while(!q.empty())
        {
            TreeNode* temp = q.front().first;
            int depth = q.front().second;
            q.pop();

            if(depth > left.size())
                left.push_back(temp->val);
            else
                left[depth-1] = max(left[depth-1], temp->val);

            if(temp->left)
                q.push(make_pair(temp->left, depth+1));

            if(temp->right)
                q.push(make_pair(temp->right, depth+1));
        }
        return left;
    }
};
