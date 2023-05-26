/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode(int x) : val(x), next(NULL) {}
 * };
 */
class Solution {
public:
    vector<ListNode*> splitListToParts(ListNode* root, int k) {
        vector<ListNode*> ans(k);

        int len = 0;
        for(ListNode* curr = root;curr; curr = curr->next, len++);

        int n = len/k, r = len%k;
        for(int i = 0;i < k && root; i++)
        {
            ans[i] = root;
            for(int j = 1;j < n+(i < r); j++)
                root = root->next;
            ListNode* temp = root->next;
            root->next = nullptr;
            root = temp;
        }
        return ans;
    }
};
