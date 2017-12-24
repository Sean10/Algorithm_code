class Solution {
public:
    bool containsNearbyDuplicate(vector<int>& nums, int k) {
        set<int> set_;
        for(int i = 0;i < nums.size(); i++)
        {

            if(i > k)
                set_.erase(nums[i-k-1]);
                // set<int>::iterator it = set_.begin();
                // for(;it != set_.end(); it++)
                //     cout << *it;
                // cout << endl;
           if(!set_.insert(nums[i]).second)
                return true;
        }
        return false;
    }
};
