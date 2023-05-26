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
    bool isPalindrome(ListNode* head) {
        if(head == NULL || head->next == NULL)
            return true;
        ListNode* fast = head->next;
        ListNode* slow = head;
        while(fast && fast->next)
        {
            slow = slow->next;
            fast = fast->next->next;
        }

        stack<int> stack_;
        while(slow->next)
        {
            slow = slow->next;
            stack_.push(slow->val);
        }
        while(!stack_.empty())
        {
            if(stack_.top() != head->val)
                return false;
            stack_.pop();
            head = head->next;
        }
        return true;

    }
};
