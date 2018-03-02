class Solution {
public:
    int getMoneyAmount(int n) {
        vector<vector<int>> dp(n+1, vector<int>(n+1));
        return helper(dp, 1, n);

    }

    int helper(vector<vector<int>>& dp, int l, int r)
    {
        if (l >= r)
            return 0;
        if (dp[l][r] != 0)
            return dp[l][r];

        int ans = INT_MAX;
        for (int i = l; i <= r; i++)
        {
            int temp = i + max(helper(dp, l, i-1), helper(dp, i+1, r));
            ans = min(ans, temp);
        }
        dp[l][r] = ans;
        return ans;
    }
};
