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
    ListNode* removeElements(ListNode* head, int val) {
        if(head == NULL)
            return head;

        ListNode dummy(INT_MIN);
        ListNode *curr = head;
        ListNode *pre = &dummy;
        while(curr)
        {
            if(curr->val == val)
            {
                pre->next = curr->next;
                free(curr);
                curr = pre;
            }else{
                pre->next = curr;
            }
            pre = curr;
            curr = curr->next;
        }
        return dummy.next;
    }
};
