class Solution {
public:
    string addBinary(string a, string b) {

        string ans;
        int i = a.size()-1, j = b.size()-1;
        int ch = 0;
        while(i>= 0 || j>= 0 || ch == 1)
        {
            ch += i >= 0 ? a[i--] -'0': 0;
            ch += j >= 0 ? b[j--] -'0': 0;
            ans.insert(0,to_string(ch%2));
            ch /= 2;
        }

        return ans;
    }
};
