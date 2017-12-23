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
    ListNode* MergeSort(ListNode* l1, ListNode* l2)
    {
        ListNode dummy(-1),*p1 = &dummy;
        dummy.next = l1;

        while(p1->next && l2)
        {
            if(p1->next->val > l2->val)
            {
                ListNode *temp = l2;
                l2 = l2->next;
                temp->next = p1->next;
                p1->next = temp;
                p1 = p1->next;
            }else
            {
                p1 = p1->next;
            }
        }
        if(l2)
        {
            p1->next = l2;
        }
        return dummy.next;
    }


    ListNode* sortList(ListNode* head) {
        if(!head || !head->next)
            return head;
        ListNode* slow = head, *fast = head->next;

        while(fast->next && fast->next->next)
        {
            slow = slow->next;
            fast = fast->next->next;
        }

        ListNode *leftHead = head, *rightHead = slow->next;
        slow->next = nullptr;
        leftHead = sortList(leftHead);
        rightHead = sortList(rightHead);

        return MergeSort(leftHead, rightHead);
    }
};
