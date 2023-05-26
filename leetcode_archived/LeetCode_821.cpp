class Solution {
public:
    vector<int> shortestToChar(string S, char C) {
        vector<int> ans;
        for (int i = 0; i < S.size(); i++)
        {
            for (int j = 0; i - j >= 0 || i + j < S.size(); j++)
            {
                if (i - j >= 0 && S[i - j] == C)
                {
                    ans.push_back(j);
                    break;
                }
                if (i + j < S.size() && S[i+j] == C)
                {
                    ans.push_back(j);
                    break;
                }
                
            }
        }
        return ans;
    }
};
