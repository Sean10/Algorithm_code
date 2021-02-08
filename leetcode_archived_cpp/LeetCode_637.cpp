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
    vector<double> averageOfLevels(TreeNode* root) {
        queue<pair<TreeNode*, int>> q;
        vector<pair<long long, int>> count;
        if (root)
            q.push(make_pair(root, 0));
        while(!q.empty())
        {
            pair<TreeNode*, int> temp = q.front();
            q.pop();
            if (temp.second == count.size())
                count.push_back(make_pair(temp.first->val, 1));
            else
                count[count.size()-1] = make_pair((count[count.size()-1].first + temp.first->val), count[count.size()-1].second+1);
            
            if (temp.first->left)
                q.push(make_pair(temp.first->left, temp.second+1));
            if (temp.first->right)
                q.push(make_pair(temp.first->right, temp.second+1));
        }
        
        vector<double> ans(count.size(), 0);
        for (int i = 0;i < ans.size(); i++)
            ans[i] = (double)count[i].first/count[i].second;
        return ans;
    }
};
