class Solution {
public:
    bool containsDuplicate(vector<int>& nums) {
        set<int> set_;
        set<int>::iterator it;
        for(int i = 0;i < nums.size();i++)
        {
            if(set_.find(nums[i]) == set_.end())
                set_.insert(nums[i]);
            else
                return true;
        }
        return false;

    }
};
