class Solution {
public:
    string reverseString(string s) {
        string::reverse_iterator l;
        string temp;
        int i = 0;
        for(l = s.rbegin(); l != s.rend(); l++)
            temp.push_back(*l);
        return temp;
    }
};
