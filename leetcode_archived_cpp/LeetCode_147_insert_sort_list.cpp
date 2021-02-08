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
    ListNode* insertionSortList(ListNode* head) {
        ListNode dummy(INT_MIN);
        ListNode *curr = head;
        ListNode *pre = &dummy;
        while(curr)
        {
            ListNode* temp = curr->next;
            pre = &dummy;
            while(pre->next && pre->next->val < curr->val)
                pre = pre->next;
            curr->next = pre->next;
            pre->next = curr;
            curr = temp;
        }
        return dummy.next;
    }
};
