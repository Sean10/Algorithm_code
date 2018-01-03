class Solution {
public:
    vector<string> letterCombinations(string digits) {
        if (digits == "")
            return {};

        const vector<string> chart = {"","","abc","def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"};
        vector<string> ans;
        helper(chart, ans, {}, digits);
        return ans;
    }

    void helper(const vector<string>& chart, vector<string>& ans, string temp, string digits)
    {
        if(digits == "")
        {
            ans.push_back(temp);
            return ;
        }

        int ch = digits[0]-'0';
        //cout << digits.front();
        digits.erase(digits.begin());
        for(int i = 0;i < chart[ch].size();i++)
        {
            temp.push_back(chart[ch][i]);
            helper(chart, ans, temp, digits);
            temp.pop_back();
        }
    }
};
