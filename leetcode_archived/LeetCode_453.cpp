class Solution {
public:
    int minMoves(vector<int>& nums) {
        int n = nums.size();
        int min_ = INT_MAX, sum = 0;
        for(auto i:nums)
        {
            min_ = min(min_,i);
            sum += i;
        }
        return sum-min_*n;
    }
};
