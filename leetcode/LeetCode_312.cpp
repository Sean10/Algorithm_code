class Solution {
public:
    int maxCoins(vector<int>& nums) {
        int n = nums.size();
        nums.insert(nums.begin(), 1);
        nums.insert(nums.end(), 1);
        vector<vector<int>> dp(n+2, vector<int>(n+2, 0));
        
        for (int len = 1; len <= n; len++)
        {
            for (int start = 1; start + len -1 <= n; start++)
            {
                int end = start + len -1;
                for (int k = start; k <= end; k++)
                    dp[start][end] = max(dp[start][end], dp[start][k-1] + nums[start-1]*nums[k]*nums[end+1] + dp[k+1][end]);
            }
        }
        return dp[1][n];
        
    }
};
