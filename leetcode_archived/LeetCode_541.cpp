class Solution {
public:
    string reverseStr(string s, int k) {
        for(int i = 0;i < s.size(); i+= 2*k)
        {
            cout << i;
            for(int j = i, l = min(i+k-1, int(s.size()-1)); j < l; j++,l--)
            {
                swap(s[j],s[l]);
                //cout << s[j] << '\t' << s[k];
            }
        }
        return s;
    }
};


class Solution {
public:
    string reverseStr(string s, int k) {
        for(int i = 0;i < s.size(); i+= 2*k)
        {
            cout << i;
            int j = i, l = min(i+k-1, int(s.size()-1));
            reverse(s.begin()+i, s.begin()+l+1);

        }
        return s;
    }
};
