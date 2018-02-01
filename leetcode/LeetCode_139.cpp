// DP
//
class Solution {
public:
    bool wordBreak(string s, vector<string>& wordDict) {
        vector<bool> dp(s.size()+1, false);
        dp[0] = true;
        int max_len = 0;
        for (auto i: wordDict)
        {
            max_len = max(max_len, int(i.size()));
        }

        for (int i = 1;i <= s.size(); i++)
            for (int j = i-1; j >= max(0, i-max_len); j--)
            {
                if(!dp[j])
                    continue;
                string word = s.substr(j, i-j);
                if (find(wordDict.begin(), wordDict.end(), word) != wordDict.end())
                {
                    dp[i] = true;
                    break;
                }

            }

        return dp[s.size()];
    }
};

//BFS

class Solution {
public:
    bool wordBreak(string s, vector<string>& wordDict) {
        queue<int> q;
        unordered_set<int> visited;

        q.push(0);
        while(q.size() > 0)
        {
            int start = q.front();
            q.pop();

            if (visited.find(start) != visited.end())
                continue;

            visited.insert(start);
            for (int i = start; i < s.size(); i++)
            {
                string word(s, start, i-start+1);
                if (find(wordDict.begin(), wordDict.end(), word) == wordDict.end())
                    continue;

                q.push(i+1);
                if (i+1 == s.size())
                    return true;

            }
        }


        return false;
    }
};
