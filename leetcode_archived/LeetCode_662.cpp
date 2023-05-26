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
    int widthOfBinaryTree(TreeNode* root) {
        return DFS(root, 0, 1, vector<int>()={});
    }

private:
    int DFS(TreeNode *root, int level, int order, vector<int>& v)
    {
        if(!root)
            return 0;
        if(v.size() == level)
            v.push_back(order);
        return max({order-v[level]+1, DFS(root->left, level+1, 2*order, v), DFS(root->right, level+1, 2*order+1, v)});
    }
};


//
//
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
    int widthOfBinaryTree(TreeNode* root) {
        int max_width = 0;
        DFS(root, 0, 1, vector<int>()={},max_width);
        return max_width;
    }

private:
    void DFS(TreeNode *root, int level, int order, vector<int>& v, int &max_width)
    {
        if(!root)
            return ;
        if(v.size() == level)
            v.push_back(order);
        max_width = max(max_width, order-v[level]+1);
        DFS(root->left, level+1, 2*order, v, max_width);
        DFS(root->right, level+1, 2*order+1, v,max_width);
    }
};
