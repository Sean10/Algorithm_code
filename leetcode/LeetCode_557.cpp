class Solution {
public:
    string reverseWords(string s) {
        int start = 0;
        for (int i = 0;i < s.size(); i++)
        {
            if(s[i] == ' ')
            {
                reverseSingle(s, start, i-1);
                start = i+1;
            }
        }
        reverseSingle(s,start, s.size()-1);
        return s;
    }

    private:
    void reverseSingle(string& s, int left, int right)
    {
        while(left < right)
        {
            swap(s[left++],s[right--]);
        }
    }
};
