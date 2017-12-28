class Solution {
public:
    string longestCommonPrefix(vector<string>& strs) {
        if(strs.size() <= 0)
            return string("");
        int len = INT_MAX;
        for(int i = 0;i < strs.size(); i++)
            len = min(len,int(strs[i].size()));
        cout << len;
        for(int i = len-1;i >= 0;i--)
        {
            char temp = strs[strs.size()-1][i];
            for(int j = 0;j < strs.size()-1; j++)
                if(temp != strs[j][i])
                {
                    len = i;
                    break;
                }
        }
        string ans;
        if(len <= 0)
            return ans;
        ans.append(strs[0].begin(),strs[0].begin()+len);
        return ans;
    }
};
