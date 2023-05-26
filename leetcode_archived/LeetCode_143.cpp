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
    void reorderList(ListNode* head) {
        if(!head || !head->next)
            return ;

        ListNode *slow = head, *fast = head;
        while(fast && fast->next)
        {
            slow = slow->next;
            fast = fast->next->next;
        }


        ListNode* tail_head = reverseList(slow->next);
        slow->next = nullptr;

        ListNode *curr = head;
        while(tail_head)
        {
            ListNode *temp1 = curr->next, *temp2 = tail_head->next;
            curr->next = tail_head;
            tail_head->next = temp1;
            tail_head = temp2;
            curr = curr->next->next;
        }
        //curr->next = nullptr;
    }

private:
    ListNode* reverseList(ListNode* head)
    {
        if(!head || !head->next)
            return head;

        ListNode dummy(INT_MIN), *pre = &dummy;
        pre->next = head;
        ListNode *curr = pre->next;

        while(curr->next)
        {
            ListNode* temp = curr->next;
            curr->next = temp->next;
            temp->next = pre->next;
            pre->next = temp;
        }

        return dummy.next;
    }
};
