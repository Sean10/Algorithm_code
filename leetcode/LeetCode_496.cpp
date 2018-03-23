// beats 99%
class Solution {
public:
    vector<int> nextGreaterElement(vector<int>& findNums, vector<int>& nums) {
        unordered_map<int, int> map_;
        for (int i = 0;i < nums.size(); i++)
        {
            map_[nums[i]] = i;
        }

        vector<int> ans;

        for (auto i: findNums)
        {
            int flag = 0;
            for (int j = map_[i]+1;j < nums.size(); j++)
            {
                if (nums[j] < i)
                    continue;
                ans.push_back(nums[j]);
                flag = 1;
                break;
            }
            if (flag == 0)
                ans.push_back(-1);
        }
        return ans;
    }
};
//

class Solution {
public:
    vector<int> nextGreaterElement(vector<int>& findNums, vector<int>& nums) {
        stack<int> stack_;
        unordered_map<int, int> map_;

        for (auto i: nums)
        {
            while (stack_.size() && stack_.top() < i)
            {
                map_[stack_.top()] = i;
                stack_.pop();
            }
            stack_.push(i);
        }

        vector<int> ans;
        for (auto i: findNums)
            ans.push_back(map_.count(i) ? map_[i] : -1);
        return ans;
    }
};
