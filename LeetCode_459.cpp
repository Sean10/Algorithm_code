# kmp
class Solution {
public:
    bool repeatedSubstringPattern(string s) {
        int n = s.size();
        vector<int> f(n+1,0);
        process(s,f);
        return f[n] && n%(n-f[n])==0;
    }

    void process(string s, vector<int> &f)
    {
        for(int i = 1; i < s.size(); i++)
        {
            int j = f[i];
            while(j && s[i] != s[j])
                j = f[j];
            f[i+1] = s[i] == s[j] ? j+1 : 0;
        }
    }
};
