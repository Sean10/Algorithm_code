class Solution {
public:
    bool isSubsequence(string s, string t) {
        int n = s.size(), j = 0;
        if(n == 0)
            return true;

        for(int i = 0; i < t.size(); i++)
        {
            if(t[i] == s[j])
                j++;
            if(j == n)
                return true;
        }
        return false;
    }
};
