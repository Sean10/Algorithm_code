//DP
class Solution {
public:
    int numberOfArithmeticSlices(vector<int>& A) {
        int n = A.size();
        int ans = 0, cnt = 0;
        vector<int> dp(n, 0);
        for (int i = 1;i < n-1; i++)
        {
            if (A[i-1] - A[i] == A[i] - A[i+1])
                dp[i+1] = dp[i]+1;
            ans += dp[i+1];
        }
        return ans;
    }
};

// Math

class Solution {
public:
    int numberOfArithmeticSlices(vector<int>& A) {
        int n = A.size();
        int ans = 0, cnt = 0;
        for (int i = 1;i < n-1; i++)
        {
            if (A[i-1] - A[i] == A[i] - A[i+1])
               ans += ++cnt;
            else
                cnt = 0;
        }
        return ans;
    }
};
