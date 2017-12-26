class Solution {
public:
    int countBinarySubstrings(string s) {
        vector<pair<int, int>> ans;
        int res = 0;
        for(int i = 1;i < s.size(); i++)
        {
            if(s[i] != s[i-1])
            {
                ans.push_back(make_pair(i-1,i));
                res++;
            }
        }

        for(int i = 0;i < ans.size(); i++)
        {
            while(ans[i].first-1 >= 0 && ans[i].second+1 < s.size() && s[ans[i].first-1] == s[ans[i].first] && s[ans[i].second+1] == s[ans[i].second])
            {
                res ++;
                ans[i].first--;
                ans[i].second++;
            }
        }
        return res;
    }
};


class Solution {
public:
    int countBinarySubstrings(string s) {
        vector<int> temp(1,1);
        for(int i = 1; i < s.size(); i++)
        {
            if(s[i] != s[i-1])
            {
                temp.push_back(1);
            }else
            {
                temp[temp.size()-1] ++;
            }
        }

        int ans = 0;
        for(int i = 1; i < temp.size(); i++)
        {
            ans += min(temp[i], temp[i-1]);
        }
        return ans;
    }
};

class Solution {
public:
    int countBinarySubstrings(string s) {
        int curr = 1, pre = 0, ans = 0;
        for(int i = 1; i < s.size(); i++)
        {
            if(s[i] != s[i-1])
            {
                ans += min(curr, pre);
                pre = curr;
                curr = 1;
            }else
            {
                curr++;
            }
        }
        ans += min(curr,pre);
        return ans;
    }
};
