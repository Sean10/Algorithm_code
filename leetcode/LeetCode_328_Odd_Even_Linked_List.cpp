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
    ListNode* oddEvenList(ListNode* head) {
        if(head == NULL)
            return head;


        ListNode* tail_odd = head;
        ListNode* curr_odd = head;
        ListNode* curr_even = head->next;
        ListNode* head_even = head->next;

        while(curr_even && curr_even->next)
        {
            curr_odd = curr_even->next;
            curr_even->next = curr_odd->next;
            curr_odd->next = head_even;
            tail_odd->next = curr_odd;
            tail_odd = curr_odd;
            curr_even = curr_even->next;
        }
        return head;
    }
};
