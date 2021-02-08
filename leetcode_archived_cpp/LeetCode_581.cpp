class Solution {
public:
    int findUnsortedSubarray(vector<int>& nums) {
        int begin = -1, end = -2, n = nums.size(), min_ = nums[n-1], max_ = nums[0];
        for (int i = 0;i < n; i++)
        {
            max_ = max(max_, nums[i]);
            min_ = min(min_, nums[n-1-i]);
            if (nums[i] < max_)
                end = i;
            if (nums[n-1-i] > min_)
                begin = n-1-i;
        }
        return end-begin+1;
    }
};
