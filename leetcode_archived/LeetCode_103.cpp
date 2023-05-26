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
    vector<vector<int>> zigzagLevelOrder(TreeNode* root) {
        vector<vector<int>> ans;
        vector<int> temp;
        deque<TreeNode*> q;
        if(!root)
            return ans;
        q.push_back(root);
        temp.push_back(root->val);
        ans.push_back(temp);


        int size_parent = 1, size_child = 0;
        bool flag = true;
        while(!q.empty())
        {
            TreeNode* curr = q.front();
            q.pop_front();

            if(curr->left)
            {
                q.push_back(curr->left);
                size_child++;
            }
            if(curr->right)
            {
                q.push_back(curr->right);
                size_child++;
            }
            size_parent--;

            if(size_parent == 0)
            {
                size_parent = size_child;
                size_child = 0;
                flag = !flag;

                temp.clear();

                if(flag)
                    for(auto i: q)
                    {
                        temp.push_back(i->val);
                    }
                else
                    for(deque<TreeNode*>::reverse_iterator it_r = q.rbegin();it_r != q.rend();it_r++)
                    {
                        temp.push_back((*it_r)->val);
                    }
                if(size_parent != 0)
                    ans.push_back(temp);
            }
        }
        return ans;

    }
};
