class Solution {
public:
    int longestPalindromeSubseq(string s) {
        vector<vector<int>> mem(s.size()+1, vector<int>(s.size()+1, 0));

        return helper(s, 0, s.size()-1, mem);

    }

    int helper(string& s, int l, int r, vector<vector<int>>& mem)
    {
        if (l == r)
            return 1;
        if (l > r )
            return 0;
        if (mem[l][r])
            return mem[l][r];
        return mem[l][r] = s[l] == s[r] ? helper(s, l+1, r-1, mem)+2 :
            max(helper(s, l, r-1, mem), helper(s, l+1, r, mem));
    }
};

class Solution {
public:
    int longestPalindromeSubseq(string s) {
        vector<vector<int>> dp(s.size()+1, vector<int>(s.size()+1, 0));

        for (int i = 0;i < s.size(); i++)
            dp[1][i] = 1;

        for (int i = 2;i <= s.size(); i++)
            for (int j = 0; i + j -1 < s.size(); j++)
            {
                dp[i][j] = s[j] == s[i+j-1] ? 2 + dp[i-2][j+1] : max(dp[i-1][j], dp[i-1][j+1]);
            }

        return dp[s.size()][0];
    }
};
