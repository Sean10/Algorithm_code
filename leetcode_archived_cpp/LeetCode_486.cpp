class Solution {
public:
    bool PredictTheWinner(vector<int>& nums) {
        int n = nums.size();
        vector<vector<int>> dp(n, vector<int>(n));

        for (int i = 0; i < n; i++)
            dp[i][i] = nums[i];

        for (int i = 1; i < n; i++)
            for (int j = 0; i+j < n; j++)
            {
                dp[j][i+j] = max(nums[j] - dp[j+1][i+j], nums[i+j] - dp[j][i+j-1]);
            }
        return dp[0][n-1] >= 0;
    }
};
