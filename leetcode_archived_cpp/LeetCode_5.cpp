class Solution {
public:
    string longestPalindrome(string s) {
        if (s.empty())
            return "";

        vector<vector<int>> dp(s.size()+1, vector<int>(s.size()+1, 0));

        for (int i = 0;i < s.size(); i++)
            dp[i][i] = 1;

        int len = 1, begin = 0;
        for (int i = s.size()-1;i >= 0; i--)
            for (int j = i; j < s.size(); j++)
            {
                if ((i+1 > j-1 || dp[i+1][j-1]) && s[j] == s[i])
                {
                    dp[i][j] = dp[i+1][j-1] + 2;
                    if (len < j-i+1)
                    {
                        len = j-i+1;
                        begin = i;
                    }
                }
            }
        // cout << len << " " << begin << endl;

        return s.substr(begin, len);
    }
};

//error
class Solution {
public:
    string longestPalindrome(string s) {
        if (s.empty())
            return "";

        vector<vector<int>> dp(s.size()+1, vector<int>(s.size()+1, 0));

        for (int i = 0;i < s.size(); i++)
            for (int j = 0;j < s.size(); j++)
                if (s[i] == s[j] )
                    dp[i][j] = 1;

        int len = 0, begin = 0;
        for (int i = 1;i < s.size(); i++)
            for (int j = 0; i + j < s.size(); j++)
            {
                if (s[j] == s[i+j])
                {
                    dp[j][i+j] = dp[j+1][i+j-1] + 2;
                    if (len < i)
                    {
                        len = i;
                        begin = j;
                    }
                }
                else
                    dp[j][i+j] = 0;
            }

        return s.substr(begin, len);
    }
};
