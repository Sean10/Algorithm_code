
class Solution {
public:
    bool isIsomorphic(string s, string t) {
        int v_s[256] = {0}, v_t[256] = {0}, n = s.size();
        for(int i = 0;i < n; i++)
        {
            if(v_s[s[i]] != v_t[t[i]])
                return false;
            v_s[s[i]] = i+1;
            v_t[t[i]] = i+1;
        }
        return true;

    }
};

// O(n) space, O(n) time
class Solution {
public:
    bool isIsomorphic(string s, string t) {
        map<char, vector<int>> map_s, map_t;
        for(int i = 0;i < s.size(); i++)
        {
            map_s[s[i]].push_back(i);
            map_t[t[i]].push_back(i);
        }

        vector<vector<int>> v_s, v_t;
        for(auto i:map_s)
            v_s.push_back(i.second);

        for(auto i:map_t)
            v_t.push_back(i.second);

        sort(v_s.begin(), v_s.end());
        sort(v_t.begin(), v_t.end());

        return v_s == v_t;

    }
};
