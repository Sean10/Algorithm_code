class Solution {
public:
    int strStr(string haystack, string needle) {
        if(needle == "") return 0;
        int ans = haystack.find(needle);
        return ans >= haystack.size() ? -1 : ans;

    }
};

# kmp

class Solution {
public:
    int strStr(string haystack, string needle) {
        int m = needle.size();

        if(m <= 0)
            return 0;

        vector<int> f(m,0);
        int j = 0;
        process(needle, f);
        for(int i = 0;i < haystack.size(); i++)
        {
            while(j && haystack[i] != needle[j])
                j = f[j];
            if(haystack[i] == needle[j])
                j++;
            if(j == m)
                return i-m+1;
        }
        return -1;
    }

    void process(string s, vector<int>& f)
    {
        for(int i = 1; i < s.size()-1; i++)
        {
            int j = f[i];
            while(j && s[i] != s[j])
                j = f[j];
            f[i+1] = s[i] == s[j] ? j+1 : 0;

        }
    }
};
