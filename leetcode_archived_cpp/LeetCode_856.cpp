class Solution {
public:
    int scoreOfParentheses(string S) {
        int ans[30] = {0}, i = 0;
        for (auto c: S)
        {
            if (c == '(')
            {
                ans[++i] = 0;
            }
            else 
            {
                ans[i-1] += max(ans[i]*2, 1);
                i--;
            }
        }
        return ans[0];
    }
};
