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
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
        stack<int> stack_1;
        stack<int> stack_2;
        ListNode dummy(INT_MIN);
        ListNode* ans = &dummy;
        ListNode* curr = NULL;
        while(l1)
        {
            stack_1.push(l1->val);
            l1 = l1->next;
        }

        while(l2)
        {
            stack_2.push(l2->val);
            l2 = l2->next;
        }

        int carry = 0;
        while(!stack_1.empty() && !stack_2.empty())
        {
            ListNode* tmp = (ListNode*)malloc(sizeof(ListNode));
            int tmp_ans = stack_1.top() + stack_2.top() + carry;
            curr = ans->next;
            tmp->val = tmp_ans%10;
            tmp->next = curr;
            carry = tmp_ans/10;
            ans->next = tmp;
            stack_1.pop();
            stack_2.pop();
        }


        while(!stack_1.empty())
        {
            ListNode *tmp = (ListNode*)malloc(sizeof(ListNode));
            curr = ans->next;
            int tmp_val = stack_1.top()+carry;
            tmp->val = tmp_val%10;
            carry = tmp_val/10;
            stack_1.pop();
            tmp->next = curr;
            ans->next = tmp;
        }
        while(!stack_2.empty())
        {
            ListNode *tmp = (ListNode*)malloc(sizeof(ListNode));
            int tmp_val = stack_2.top()+carry;
            curr = ans->next;
            tmp->val = tmp_val%10;
            carry = tmp_val/10;
            stack_2.pop();
            tmp->next = curr;
            ans->next = tmp;
        }
        if(stack_1.empty() && stack_2.empty() && carry)
        {
            ListNode *tmp = (ListNode*)malloc(sizeof(ListNode));
            curr = ans->next;
            tmp->val = carry;
            tmp->next = curr;
            ans->next = tmp;
        }
        return dummy.next;
    }
};
