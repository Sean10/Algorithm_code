class Solution {
public:
    vector<string> letterCasePermutation(string S) {
        set<string> ans;
        helper(ans, 0, S);
        return vector<string>(ans.begin(), ans.end());
    }

    void helper(set<string>& ans, int start, string S)
    {
        // cout << S << endl;
        ans.insert(S);
        for (int i = start;i < S.size(); i++)
        {
            string temp = S;
            if (isdigit(S[i])) continue;
            if (islower(S[i]))
                temp[i] = toupper(temp[i]);
            else
                temp[i] = tolower(temp[i]);
            // cout << temp << endl;
            helper(ans, i+1, temp);
        }

    }
};
