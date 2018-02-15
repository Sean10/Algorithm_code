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
    vector<int> rightSideView(TreeNode* root) {
        vector<int> ans;
        recursion(ans, 1, root);
        return ans;
    }

private:
    void recursion(vector<int>& ans, int level, TreeNode* root)
    {
        if (!root)
            return ;
        if (ans.size() < level) ans.push_back(root->val);
        recursion(ans, level+1, root->right);
        recursion(ans, level+1, root->left);
    }

};

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
    vector<int> rightSideView(TreeNode* root) {
        queue<pair<TreeNode*, int>> q;
        vector<int> ans;
        if (root)
            q.push(make_pair(root, 0));
        while(!q.empty())
        {
            TreeNode* temp = q.front().first;
            int depth = q.front().second;
            q.pop();

            if (temp->left)
                q.push(make_pair(temp->left, depth+1));

            if (temp->right)
                q.push(make_pair(temp->right, depth+1));

            if (q.empty() || depth != q.front().second)
                ans.push_back(temp->val);
        }
        return ans;
    }
};
