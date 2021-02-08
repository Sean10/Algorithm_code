class Solution {
public:
    vector<string> generateParenthesis(int n) {
        vector<string> ans;
        helper("", ans, n, 0);
        return ans;
    }

    void helper(string str, vector<string>& ans, int left, int right)
    {
        if(left <= 0 && right <= 0)
        {
            ans.push_back(str);
            return ;
        }

        if(left > 0)
            helper(str+"(", ans, left-1, right+1);
        if(right > 0)
            helper(str+")", ans, left, right-1);

    }
};
