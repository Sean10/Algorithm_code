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
    ListNode* swapPairs(ListNode* head) {
        if(head == NULL || head->next == NULL)
            return head;
        ListNode* ans = head->next;
        ListNode* curr = head;
        ListNode* temp;
        //cout << curr->val << endl;
        ListNode* pre = NULL;
        while(curr&&curr->next)
        {
            if(pre)
            {
                pre->next = curr->next;
            }
            pre = curr;
            temp = curr->next;
            curr->next = temp->next;
            temp->next = curr;
            //cout << curr->val << endl;

            curr = curr->next;

        }
        return ans;
    }
};
