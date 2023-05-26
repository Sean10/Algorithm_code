class Solution {
public:
    bool checkVowel(char temp)
    {
        temp = tolower(temp);
        switch(temp)
        {
            case 'a':
            case 'e':
            case 'o':
            case 'i':
            case 'u':
                return true;
            default:
                return false;
        }
    }

    string reverseVowels(string s) {
        int it = 0;
        int it_r = s.size()-1;
        while(it < it_r)
        {
            if(checkVowel(s[it]) && checkVowel(s[it_r]))
            {
                char temp = s[it];
                s[it] = s[it_r];
                s[it_r] = temp;
                it++;
                it_r--;
                cout << s[it] << s[it_r];
            }
            else if(!checkVowel(s[it]))
                it++;
            else if(!checkVowel(s[it_r]))
                it_r--;
        }
        return s;
    }
};
