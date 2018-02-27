class Solution {
public:
    int findTargetSumWays(vector<int>& nums, int S) {
        int sum = accumulate(nums.begin(), nums.end(), 0);
        return sum < S || (sum+S)&1 ? 0 : subset(nums, (sum + S) >> 1);
    }

    int subset(vector<int>& nums, int sum)
    {
        vector<int> dp(sum+1, 0);
        dp[0] = 1;
        for (auto n: nums)
        {
            for (int i = sum; i >= n; i--)
                dp[i] += dp[i - n];
        }
        return dp[sum];
    }
};
