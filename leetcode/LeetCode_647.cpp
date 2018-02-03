

class Solution {
public:
    int countSubstrings(string s) {
        int n = s.size();

        int ans = 0;
        for(int i = 0;i < n; i++)
        {
            for (int j = 0; i-j >= 0 && i+j < n && s[i-j] == s[i+j];j++) ans++;
            for (int j = 0; i-1-j >= 0 && i+j < n && s[i-1-j] == s[i+j];j++) ans++;
        }
        return ans;
    }
};

// DP

class Solution {
public:
    int countSubstrings(string s) {
        int n = s.size();

        vector<vector<int>> dp;
        for(int i = 0;i < n;i++)
        {
            vector<int> temp(n, 0);
            dp.push_back(temp);
        }

        int ans = 0;
        for(int i = n-1;i >= 0; i--)
        {
            for(int j = i; j < n;j++)
            {
                dp[i][j] = s[i] == s[j] && (j-i < 3 || dp[i+1][j-1]);
                if (dp[i][j])
                    ans++;
            }
        }
        return ans;
    }
};
