class Solution {
public:
    bool detectCapitalUse(string word) {
        if(word.size() < 2) return true;
        int flag = !isupper(word[0]) ? 0 : isupper(word[1]) ? 2 : 1 ;
        for(int i = 1;i < word.size() ;i++)
        {
            if(flag == 0 || flag == 1)
            {
                if(isupper(word[i]))
                    return false;
            }
            else if(flag == 2)
            {
                if(islower(word[i]))
                    return false;
            }

        }
        return true;
    }
};
