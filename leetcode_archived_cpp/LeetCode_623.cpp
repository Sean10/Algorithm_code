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
    TreeNode* addOneRow(TreeNode* root, int v, int d) {
        queue<pair<TreeNode*, int>> q;
        TreeNode* head = new TreeNode(0);
        head->left = root;
        q.push(make_pair(head, 0));
        while(!q.empty())
        {
            TreeNode *curr = q.front().first;
            int depth = q.front().second;
            q.pop();

            if(curr == nullptr)
                continue;

            // if (curr->left)
            q.push(make_pair(curr->left, depth+1));
            // if (curr->right)
            q.push(make_pair(curr->right, depth+1));

            if (depth == d-1)
            {
                TreeNode* left = new TreeNode(v);
                left->left = curr->left;
                curr->left = left;
                TreeNode* right = new TreeNode(v);
                right->right = curr->right;
                curr->right = right;
            }
        }
        return head->left;
    }
};
