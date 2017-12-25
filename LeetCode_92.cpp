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
    ListNode* reverseBetween(ListNode* head, int m, int n) {
        ListNode dummy(INT_MIN), *pre= &dummy;
        pre->next = head;
        for(int i = 0;i < m-1;i++)
        {
            pre = pre->next;
        }

        ListNode* curr = pre->next;
        for(int i = m;i < n;i++)
        {
            ListNode *temp = curr->next;
            curr->next = temp->next;
            temp->next = pre->next;
            pre->next = temp;
        }

        return dummy.next;
    }
};
