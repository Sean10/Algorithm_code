# DFS版本

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
    TreeNode* buildTree(vector<int>& preorder, vector<int>& inorder) {
        TreeNode* p = nullptr;
        DFS(p, preorder, inorder, 0, 0, preorder.size());

        return p;
    }

    int Position(vector<int>& v, int val)
    {
        for(int i = 0;i < v.size(); i++)
            if(v[i] == val)
                return i;
        return 0;
    }

    void DFS(TreeNode* &p, vector<int>& preorder, vector<int>& inorder, int i, int j, int len)
    {
        if(len <= 0)
            return ;

        p = new TreeNode(preorder[i]);
        int pos = Position(inorder, preorder[i]);
        DFS(p->left, preorder, inorder, i+1, j, pos-j);
        DFS(p->right, preorder, inorder, i+pos-j+1, pos+1, len-1-(pos-j));
    }
};

# 使用随机迭代器，存在一些理论上的问题

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
    TreeNode* buildTree(vector<int>& preorder, vector<int>& inorder) {
        iterator<random_access_iterator_tag, int> pos = find(inorder.begin(), inorder.end(), *preorder.begin());
        iterator<random_access_iterator_tag, int> j = inorder.begin();
        iterator<random_access_iterator_tag, int> i = preorder.begin();
        TreeNode* p;
        DFS(p, preorder, inorder, i+1, j, pos-j);
        DFS(p, preorder, inorder, i+pos-j+1, pos+1, pos-j);
    }

    void DFS(TreeNode* p, vector<int>& preorder,vector<int>& inorder, iterator<random_access_iterator_tag, int> i, iterator<random_access_iterator_tag, int> j, int len)
    {
        if(len <= 0)
            return ;

        p = new TreeNode(*i.val);
        vector<int>::iterator pos = find(i, inorder.end(), *i);
        DFS(p->left, preorder, inorder, i+1, j, pos-j);
        DFS(p->right, preorder, inorder, i+pos-j+1, pos+1, pos-j);

    }
};
