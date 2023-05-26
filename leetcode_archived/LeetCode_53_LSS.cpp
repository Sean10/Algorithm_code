class Solution {
public:
    int maxSubArray(vector<int>& nums) {

        int len = nums.size();
        vector<int> dp(len,nums[0]);
        int sum_max = nums[0];
        for(int i = 1;i < len;i++)
        {
            if(dp[i-1] > 0)
                dp[i] = dp[i-1] + nums[i];
            else
                dp[i] = nums[i];
            sum_max = max(sum_max, dp[i]);
        }
        return sum_max;
    }
};
