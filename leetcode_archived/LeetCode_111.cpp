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
    int minDepth(TreeNode* root) {
        queue<pair<TreeNode*,int>> q;

        if (root)
            q.push(make_pair(root,1));

        while(!q.empty())
        {
            TreeNode* temp = q.front().first;
            int depth = q.front().second;
            q.pop();
            cout << depth << endl;
            if(temp->left == nullptr && temp->right == nullptr)
                return depth;
            if (temp->left)
                q.push(make_pair(temp->left,depth+1));
            if (temp->right)
                q.push(make_pair(temp->right,depth+1));
        }
        return 0;
    }
};
