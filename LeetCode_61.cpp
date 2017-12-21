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
    ListNode* rotateRight(ListNode* head, int k) {
        if(k == 0 || !head || !head->next)
            return head;

        ListNode dummy(0);
        ListNode* left = &dummy;
        left->next = head;

        int len = 0;
        ListNode* curr = head;
        while(curr)
        {
            curr = curr->next;
            len ++;
        }
        //cout << len+1;
        if(k >= len)
            k = k%(len);

        while(k--)
        {
            ListNode* tail = nullptr, *pre = nullptr;
            curr = head;
            while(curr->next && curr->next->next)
            {
                curr = curr->next;
            }
            pre = curr;
            tail = curr->next;

            tail->next = left->next;
            left->next = tail;
            pre->next = nullptr;
        }
        return dummy.next;
    }
};
