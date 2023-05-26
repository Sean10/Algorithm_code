class Solution {
public:
    vector<vector<string>> partition(string s) {
        if(s.empty())
            return {};
        vector<vector<string>> ans;
        helper(s,{},ans, 0);
        return ans;
    }

    void helper(string s, vector<string> temp, vector<vector<string>>& ans, int start)
    {
        if(start == s.size())
        {
            ans.push_back(temp);
            return ;
        }

        for(int i = start; i < s.size();i++)
        {
            if(isPalindrome(s, start, i))
            {
                temp.push_back(s.substr(start, i-start+1));
                helper(s, temp, ans, i+1);
                temp.pop_back();
            }
        }
    }

    bool isPalindrome(string s, int start, int end)
    {
        while(start < end)
        {
            if(s[start++] != s[end--])
                return false;
        }
        return true;
    }
};
