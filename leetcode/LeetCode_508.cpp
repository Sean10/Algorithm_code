// 一开始直接用map，结果不稳定，不会按原始顺序得到结果，只好换成unordered_map

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
    vector<int> findFrequentTreeSum(TreeNode* root) {
        unordered_map<int, int> map_;

        if(root)
            count(map_, root);

        int max_count = 0;
        for(auto i: map_)
            max_count = max(i.second, max_count);

        vector<int> ans;
        for(auto i:map_)
        {
            if (i.second == max_count)
                ans.insert(ans.begin(), i.first);
        }
        return ans;
    }

    int count(unordered_map<int, int>& map_, TreeNode* root)
    {
        int sum = root->val;
        sum += root->left ? count(map_, root->left) : 0;
        sum += root->right ? count(map_, root->right) : 0;

        map_[sum]++;

        return sum;
    }
};
