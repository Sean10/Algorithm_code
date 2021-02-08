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
    int GetLength(ListNode* head)
    {
        int length = 0;
        while(head)
        {
            head = head->next;
            length++;
        }
        return length;
    }

    ListNode* removeNthFromEnd(ListNode* head, int n) {
        if(head == NULL || head->next == NULL && n == 1)
            return NULL;

        int pos = GetLength(head) - n;


        //cout << pos << endl;
        int tmp_pos = 0;
        ListNode* pre = head;
        ListNode* curr = head;
        if(pos == 0)
        {
            curr = head->next;
            free(pre);
            return curr;
        }
        while(tmp_pos < pos)
        {
            tmp_pos++;
            pre = curr;
            curr = curr->next;
        }
        pre->next = curr->next;
        free(curr);
        return head;
    }
};
