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
    bool hasCycle(ListNode *head) {
        if(head == NULL || head->next == NULL)
            return false;
        ListNode* walk = head;
        ListNode* run = head->next;
        while(run && run->next)
        {
            if(walk == run)
                return true;
            walk = walk->next;
            run = run->next->next;
        }
        return false;

    }
};
