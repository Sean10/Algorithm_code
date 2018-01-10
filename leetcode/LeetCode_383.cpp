class Solution {
public:
    bool canConstruct(string ransomNote, string magazine) {
        vector<int> ch(255,0);
        for(int i = 0;i < magazine.size(); i++)
            ch[magazine[i]] ++;
        for(int i = 0;i < ransomNote.size(); i++)
        {
            if(--ch[ransomNote[i]] < 0)
                return false;
            //ch[[i]]--;
        }
        return true;
    }
};
