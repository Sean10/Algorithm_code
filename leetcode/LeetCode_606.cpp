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
    string tree2str(TreeNode* t) {
        string ans;
        DFS(t, ans);
        return ans;

    }

    void DFS(TreeNode* root, string &ans)
    {
        if(!root)
            return ;
        //cout << root->val;
        string ch = to_string(root->val);
        ans.append(ch);
        if(root->left || root->right)
        {
            ans.push_back('(');
            DFS(root->left, ans);
            ans.push_back(')');
        }
        if(root->right)
        {
            ans.push_back('(');
            DFS(root->right, ans);
            ans.push_back(')');
        }
    }
};
