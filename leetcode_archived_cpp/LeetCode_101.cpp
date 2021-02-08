/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode(int x) : val(x), left(NULL), right(NULL) {}
 * };
 */
class Solution {
public:
    bool isSymmetric(TreeNode* root) {
        queue<TreeNode*> q;
        q.push(root);
        q.push(root);
        while(!q.empty())
        {
            TreeNode* t1 = q.front();
            q.pop();
            TreeNode* t2 = q.front();
            q.pop();
            if(t1 == nullptr && t2 == nullptr) continue;
            if(t1 == nullptr || t2 == nullptr) return false;
            if(t1->val != t2->val) return false;
            q.push(t1->left);
            q.push(t2->right);
            q.push(t1->right);
            q.push(t2->left);
        }
        return true;
    }


};


# second way

/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode(int x) : val(x), left(NULL), right(NULL) {}
 * };
 */
class Solution {
public:
    bool isSymmetric(TreeNode* root) {
        deque<TreeNode*> stack_;
        TreeNode* curr = root;

        if(curr)
            stack_.push_back(curr);

        int level = 2;
        int curr_level = 0;

        shared_ptr<TreeNode> ptr_null(new TreeNode(0));
        while(!stack_.empty())
        {
            //cout << curr->val << endl;
            curr = stack_.front();
            stack_.pop_front();

            if(curr->left)
            {
                stack_.push_back(curr->left);
            }else
            {
                stack_.push_back(ptr_null.get());
            }

            if(curr->right)
            {
                stack_.push_back(curr->right);
            }else
            {
                stack_.push_back(ptr_null.get());
            }
            curr_level += 2;

            cout << curr_level << ' '<<level << endl;
            for(deque<TreeNode*>::iterator it_t = stack_.begin(); it_t != stack_.end(); it_t++)
                cout << (*it_t)->val << ' ';
            cout << endl;

            if(level == curr_level)
            {
                curr_level = 0;
                deque<TreeNode*>::iterator it;

                // for(it = stack_.begin(); it != stack_.end(); it++)
                //     cout << (*it)->val << "";
                // cout << endl;

                int cnt = 0;
                deque<TreeNode*>::reverse_iterator it_r;
                int temp_lv = level/2;
                for(it = stack_.begin(), it_r = stack_.rbegin();\
                   cnt < temp_lv; cnt++)
                {
                    // cout << cnt << ' '<< level/4 <<endl;
                    // for(deque<TreeNode*>::iterator it_t = stack_.begin(); it_t != stack_.end(); it_t++)
                    //     cout << (*it_t)->val << "";
                    // cout << endl;

                    if((*it) == ptr_null.get() && ptr_null.get() == (*it_r))
                    {
                        it = stack_.erase(it);
                        it_r = deque<TreeNode*>::reverse_iterator(stack_.erase(next(it_r).base()));
                        level -= 2;
                        continue;
                    }

                    if((*it)->val == (*it_r)->val)
                    {
                        cout << cnt << ' '<<temp_lv << endl;

                        cout << (*it)->val << " " << *it << " "<< (*it_r)->val << " " << *it_r << endl;
                         it++;
                        it_r++;
                        continue;
                    }
                    else
                    {
                        cout << cnt << ' '<< temp_lv << endl;
                        cout << (*it)->val << " " << *it << " "<< (*it_r)->val << " " << *it_r << endl;
                        return false;
                    }
                }
                level *= 2;
            }
        }
        return true;
    }


};
