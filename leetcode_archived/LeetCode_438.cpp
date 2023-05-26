class Solution {
public:
    vector<int> findAnagrams(string s, string p) {
        vector<int> pv(26, 0), sv(26, 0), ans;
        if (s.size() < p.size())
            return ans;

        for (int i = 0;i < p.size(); i++)
        {
            ++pv[p[i] - 'a'];
            ++sv[s[i] - 'a'];
        }

        if (pv == sv)
            ans.push_back(0);

        for (int i = p.size(); i < s.size(); i++)
        {
            ++ sv[s[i] - 'a'];
            -- sv[s[i - p.size()] - 'a'];
            if (sv == pv)
                ans.push_back(i - p.size() + 1);
        }
        return ans;


    }
};
