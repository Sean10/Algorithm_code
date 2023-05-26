/**
 * Definition for singly-linked list with a random pointer.
 * struct RandomListNode {
 *     int label;
 *     RandomListNode *next, *random;
 *     RandomListNode(int x) : label(x), next(NULL), random(NULL) {}
 * };
 */
class Solution {
public:
    RandomListNode *copyRandomList(RandomListNode *head)
    {
        RandomListNode *iter = head, *next;

        while(iter)
        {
            next = iter->next;

            RandomListNode *copy = new RandomListNode(iter->label);
            copy->next = next;
            iter->next = copy;

            iter = next;
        }

        iter = head;
        while(iter)
        {
            if(iter->random)
            {
                iter->next->random = iter->random->next;
            }
            iter = iter->next->next;
        }

        iter = head;
        RandomListNode dummy(INT_MIN), *ptr = &dummy;
        while(iter)
        {
            next = iter->next->next;

            ptr->next = iter->next;
            ptr = ptr->next;

            iter->next = next;
            iter = next;
        }
        return dummy.next;
    }
};



// hashmap
/**
 * Definition for singly-linked list with a random pointer.
 * struct RandomListNode {
 *     int label;
 *     RandomListNode *next, *random;
 *     RandomListNode(int x) : label(x), next(NULL), random(NULL) {}
 * };
 */
class Solution {
public:
    RandomListNode *copyRandomList(RandomListNode *head) {
        if(!head)
            return nullptr;
        map<RandomListNode*,RandomListNode*> map_;
        RandomListNode *new_head = new RandomListNode(head->label);
        map_[head] = new_head;
        new_head->next = copyRandomList2(head->next,map_);
        new_head->random = copyRandomList2(head->random, map_);
        return new_head;
    }

private:
    RandomListNode *copyRandomList2(RandomListNode *head, map<RandomListNode*,RandomListNode*> &map_)
    {
        if(!head)
            return nullptr;
        else if(map_.find(head) != map_.end())
            return map_[head];
        RandomListNode *new_head = new RandomListNode(head->label);
        map_[head] = new_head;
        new_head->next = copyRandomList2(head->next,map_);
        new_head->random = copyRandomList2(head->random, map_);
        return new_head;
    }
};
