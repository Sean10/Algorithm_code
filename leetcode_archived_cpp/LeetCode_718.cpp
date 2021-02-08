class Solution {
public:
    int findLength(vector<int>& A, vector<int>& B) {
        int m = A.size(), n = B.size();
        vector<vector<int>> dp(m+1, vector<int>(n+1, 0));
        
        int max_ = INT_MIN;
        for (int i = 1; i <= m; i++)
            for (int j = 1; j <= n; j++)
            {
                dp[i][j] = A[i-1] == B[j-1] ? dp[i-1][j-1]+1 : dp[i][j];
                max_ = max(max_, dp[i][j]);
            }
        return max_;
    }
    
};
