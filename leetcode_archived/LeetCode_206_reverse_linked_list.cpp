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
    ListNode* reverseList(ListNode* head) {
        if(head == NULL || head->next == NULL)
            return head;

        ListNode* curr;
        curr = head->next;
        head->next = NULL;

        while(curr->next)
        {
            ListNode* temp = curr->next;
            curr->next = head;
            head = curr;
            curr = temp;
        }
        curr->next = head;
        return curr;
    }
};


// /**
//  * Definition for singly-linked list.
//  * struct ListNode {
//  *     int val;
//  *     ListNode *next;
//  *     ListNode(int x) : val(x), next(NULL) {}
//  * };
//  */
// class Solution {
// public:
//     ListNode* reverseList(ListNode* head) {
//         ListNode* curr = NULL;
//
//         while(head)
//         {
//             ListNode* temp = head->next;
//             head->next= curr;
//             curr = head;
//             head = temp;
//         }
//         return curr;
//     }
// };
