class Solution {
public:
    int firstUniqChar(string s) {
        map<char, int> ch;
        for(int i = 0;i < s.size(); i++)
        {
            ch[s[i]]++;
        }

        for(auto i = 0; i < s.size(); i++)
            if(ch[s[i]] == 1)
                return i;
        return -1;
    }
};
