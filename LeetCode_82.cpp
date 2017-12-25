// recursive

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
        if(!head || !head->next)
            return head;

        ListNode* pre = head->next;
        int val = head->val;

        if(val != pre->val)
        {
            head->next = deleteDuplicates(pre);
            return head;
        }else
        {
            while(pre && pre->val == val)
                pre = pre->next;
            return deleteDuplicates(pre);
        }
    }
};


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
        if(!head || !head->next)
            return head;

        ListNode dummy(INT_MIN), *pre = &dummy;
        pre->next = head;
        ListNode *curr = pre->next;
        while(curr)
        {
            ListNode *next = curr->next;
            if(next && curr->val == next->val)
            {
                while(next && curr->val == next->val)
                    next = next->next;
                curr = next;
                pre->next = curr;
            }else
            {
                pre = curr;
                curr = curr->next;
            }
        }
        return dummy.next;
    }
};
