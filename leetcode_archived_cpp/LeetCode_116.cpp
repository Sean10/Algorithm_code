# 普通迭代

/**
 * Definition for binary tree with next pointer.
 * struct TreeLinkNode {
 *  int val;
 *  TreeLinkNode *left, *right, *next;
 *  TreeLinkNode(int x) : val(x), left(NULL), right(NULL), next(NULL) {}
 * };
 */
class Solution {
public:
    void connect(TreeLinkNode *root) {
        if(!root)
            return ;

        TreeLinkNode *head = root;
        TreeLinkNode *pre = nullptr;
        TreeLinkNode *curr = root;
        while(head->left)
        {
            curr->left->next = curr->right;
            if(pre)
                pre->right->next = curr->left;
            if(curr->next == nullptr)
            {
                head = head->left;
                pre = nullptr;
                curr = head;
            }
            else
            {
                pre = curr;
                curr = curr->next;
            }
        }
    }
};
