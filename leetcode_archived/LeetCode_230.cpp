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
    int kthSmallest(TreeNode* root, int k) {
        TreeNode *ans = nullptr;
        kthSearch(root, ans, k);
        return ans->val;
    }

    void kthSearch(TreeNode *root, TreeNode *&ans, int &k)
    {
        if(!root)
            return ;
        if(root->left)
            kthSearch(root->left, ans, k);
        if(--k == 0)
            ans = root;
        //cout << k << '\t' << root->val << ans->val;
        if(root->right)
            kthSearch(root->right, ans ,k);
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
    int kthSmallest(TreeNode* root, int k) {
        vector<int> temp;
        tempVector(temp, root);
        sort(temp.begin(), temp.end());

        return temp[k-1];
    }

    void tempVector(vector<int> &temp, TreeNode *root)
    {
        if(! root)
            return ;
        temp.push_back(root->val);
        tempVector(temp, root->left);
        tempVector(temp, root->right);
    }
};
