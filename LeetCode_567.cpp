class Solution {
public:
    bool checkInclusion(string s1, string s2) {
        if(s1.size() > s2.size())
            return false;
        vector<int> char1(26,0),char2(26,0);
        for(int i = 0;i < s1.size(); i++)
        {
            char1[s1[i]-'a']++;
            char2[s2[i]-'a']++;
        }

        if(char1 == char2) return true;
        for(int i = 0;i+s1.size() < s2.size(); i++)
        {
            char2[s2[i]-'a']--;
            char2[s2[i+s1.size()]-'a']++;
            if(char1 == char2) return true;

        }
        return false;
    }
};
