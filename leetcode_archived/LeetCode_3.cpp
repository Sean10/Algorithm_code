class Solution {
public:
    int lengthOfLongestSubstring(string s) {
        vector<int> charIndex(256, -1);
        int len = 0, max_len = 0;
        int n = s.size();
        for(int i = 0;i < n;i++)
        {
            len = max(charIndex[s[i]]+1, len);
            charIndex[s[i]] = i;
            max_len = max(max_len, i-len+1);
        }
        return max_len;
    }
};
