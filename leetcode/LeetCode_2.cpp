/*
leetCode 2
一开始这道题都没看懂，看了一下其他人的解答，才知道这2个链表对应的只是2个数，所以要处理成完整的数以后加起来才得到结果。
1. 第一次提交时，出现WA，意识到不能先计算成数再累加，遇到大数就无法正确处理了，需要做成链表的累加方法。
    两个链表不一定一样长，某一个结束以后，根据进位条件修改完下一个之后，其他都可以直接剪切了

    第二次提交，结果还是忘了最后一位有进位时要创建新节点……

2. 除了大数，还会有什么边界情况呢？似乎是没有了，题目中也写到了是非负.

看了Solution……我的思路太没结构了……居然那么简单


 */


#include <iostream>
#include <stack>
#include <vector>

using namespace std;

/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode(int x) : val(x), next(NULL) {}
 * };
 */

struct ListNode {
    int val;
    ListNode *next;
    ListNode(int x) : val(x), next(NULL){}
};

 class Solution {
 public:
     ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
         ListNode* ans = new ListNode(0);
         int carry = 0;
         ListNode* p = l1;
         ListNode* q = l2;
         ListNode* curr = ans;
         while(p != NULL || q != NULL)
         {
             int x = (p != NULL) ? p->val : 0;
             int y = (q != NULL) ? q->val : 0;
             int sum = carry + x+ y;
             carry = sum/10;
             curr->next = new ListNode(sum%10);
             curr = curr->next;
             if(p != NULL) p = p->next;
             if(q != NULL) q = q->next;
         }
         if(carry > 0)
         {
             curr->next = new ListNode(carry);
         }
         return ans->next;
     }


        //  int carry = 0;
         //
        //  ListNode* ans_list = new ListNode(0);
        //  ListNode* curr_ans = ans_list;
         //
        //  int head_sum = l1->val + l2->val;
         //
         //
        //  if(head_sum >= 10)
        //  {
        //      carry = 1;
        //  }
         //
        //  ans_list->val = head_sum%10;
        //  ans_list->next = NULL;
         //
        //  ListNode* curr_l1 = l1->next;
        //  ListNode* curr_l2 = l2->next;
         //
         //
        //  int tmp_sum = 0;
        //  while(curr_l1 != NULL && curr_l2 != NULL)
        //  {
        //      ListNode* p = new ListNode(0);
         //
        //      tmp_sum = curr_l1->val + curr_l2->val + carry;
         //
        //      if(tmp_sum >= 10)
        //      {
        //          carry = 1;
        //      }else
        //      {
        //          carry = 0;
        //      }
         //
        //      p->val = tmp_sum%10;
        //      p->next = NULL;
        //      curr_ans->next = p;
        //      curr_ans = p;
         //
        //      curr_l1 = curr_l1->next;
        //      curr_l2 = curr_l2->next;
        //  }
         //
        //  if(curr_l1 == NULL && curr_l2 == NULL && carry == 1)
        //  {
        //      ListNode* p = new ListNode(0);
        //      p->val = 1;
        //      p->next = NULL;
        //      curr_ans->next = p;
        //  }
        //  else if(curr_l2 == NULL || curr_l1 == NULL)
        //  {
        //      if(curr_l2 == NULL)
        //      {
        //          curr_ans->next = curr_l1;
        //      }
        //      else if(curr_l1 == NULL)
        //      {
        //          curr_ans->next = curr_l2;
        //      }
         //
        //      while(carry)
        //      {
        //          int tmp_sum;
         //
        //          if(curr_ans->next == NULL)
        //          {
        //              tmp_sum = carry;
        //              ListNode* p = new ListNode(0);
        //              p->val = tmp_sum;
        //              p->next = NULL;
        //              curr_ans->next = p;
        //              curr_ans = curr_ans->next;
        //          }
        //          else
        //          {
        //              curr_ans = curr_ans->next;
        //              tmp_sum = curr_ans->val + carry;
        //              curr_ans->val = tmp_sum%10;
        //          }
         //
        //          //cout << __LINE__ << " "<< tmp_sum << endl;
         //
         //
        //          if(tmp_sum >= 10)
        //          {
        //              carry = 1;
        //          }else{
        //              carry = 0;
        //          }
        //          //curr_ans = curr_ans->next;
        //      }
        //  }
         //
        //  return ans_list;
        //  }

 };

class test
{
public:
    void SetList(vector<int> &tmp, ListNode* list)
    {
        //list = new ListNode(0);
        list->val = tmp[0];
        list->next = NULL;
        ListNode* curr = list;

        for(int i = 1; i < tmp.size(); i++)
        {
            ListNode *p = new ListNode(0);
            p->val = tmp[i];
            p->next = NULL;
            curr->next = p;
            curr = p;
        }
    }
};

int main(void)
{
	Solution sol;
    test test_set;

    ListNode* l1 = new ListNode(0);
    ListNode* l2 = new ListNode(0);
    ListNode* ans;


    int tmp[] = {9,8};
    //vector_1 = tmp;
    vector<int> vector_1(begin(tmp), end(tmp));

    int tmp2[] = {1};
    //vector_2 = tmp;
    vector<int> vector_2(begin(tmp2), end(tmp2));

    test_set.SetList(vector_1,l1);
    test_set.SetList(vector_2,l2);


    ans = sol.addTwoNumbers(l1, l2);

    while(ans != NULL)
    {
        cout << ans->val << endl;
        ans = ans->next;
    }


}
