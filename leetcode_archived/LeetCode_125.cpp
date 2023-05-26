class Solution {
public:
    bool isPalindrome(string s) {
        string::iterator it = s.begin();
        string::reverse_iterator it_r = s.rbegin();
        locale loc;
        while(it != s.end() && it_r != s.rend())
        {
            if(!isalnum(*it, loc))
                it++;
            else if(!isalnum(*it_r, loc))
                it_r++;
            else if(tolower(*it) != tolower(*it_r))
                return false;
            else
            {
                it++;
                it_r++;
            }

        }
        return true;
    }
};
