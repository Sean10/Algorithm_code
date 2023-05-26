class Solution {
public:
    int majorityElement(vector<int>& nums) {
        map<int,int> map_;
        for(int i = 0;i < nums.size();i++)
        {
            if(++map_[nums[i]] > nums.size()/2)
                return nums[i];
        }


    }
};
