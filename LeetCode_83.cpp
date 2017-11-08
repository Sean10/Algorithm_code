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
    ListNode* deleteDuplicates(ListNode* head) {
        if(head == NULL || head->next == NULL)
            return head;
        ListNode *curr = head->next;
        ListNode *pre = head;
        while(curr)
        {
            if(pre->val == curr->val)
            {
                pre->next = curr->next;
            }else{
                pre = pre->next;
            }
            curr = curr->next;
        }
        return head;
    }
};
