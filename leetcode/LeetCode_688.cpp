class Solution {
public:
    double knightProbability(int N, int K, int r, int c) {
        vector<vector<vector<double>>> dp(K+1, vector<vector<double>>(N, vector<double>(N, -1.0)));
        return helper(dp, N, K, r, c)/pow(8, K);
    }
    
    double helper(vector<vector<vector<double>>>& dp, int N, int K, int r, int c)
    {
        if (r < 0 || r >= N || c < 0 || c >= N)
            return 0;
        if (K == 0)
            return 1;
        if (dp[K][r][c] != -1.0)
            return dp[K][r][c];
        dp[K][r][c] = 0.0;
        for (int i = 0; i < 8; i++)
            dp[K][r][c] += helper(dp, N, K-1, r+dir[i][0], c+dir[i][1]);
        return dp[K][r][c];
    }
    
private:
    vector<vector<int>> dir = {{1, 2}, {1, -2}, {-1, 2}, {-1, -2}, {2, 1}, {-2, 1}, {2, -1}, {-2, -1}};
};
