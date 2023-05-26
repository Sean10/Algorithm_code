class Solution {
public:
    vector<int> findSubstring(string s, vector<string>& words) {
        unordered_map<string, int> count;
        for (auto word: words)
            count[word]++;

        int n = s.size(), num = words.size(), len = words[0].size();
        vector<int> ans;
        for (int i = 0; i < n - num*len + 1; i++)
        {
            unordered_map<string, int> seen;
            int j = 0;
            for (; j < num; j++)
            {
                string word = s.substr(i+j*len, len);
                if (count.find(word) != count.end())
                {
                    seen[word]++;
                    if (seen[word] > count[word])
                        break;
                }
                else
                    break;
            }
            if (num == j)
                ans.push_back(i);
        }
        return ans;
    }
};
