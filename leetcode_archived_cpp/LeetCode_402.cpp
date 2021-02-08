class Solution {
public:
    string removeKdigits(string num, int k) {
        string ans = "";

        for (char i: num)
        {
            while (ans.length() && ans.back() > i && k)
            {
                ans.pop_back();
                k--;
            }

            if (ans.length() || i != '0')
                ans.push_back(i);
        }

        while (ans.length() && k--)
            ans.pop_back();

        return ans.empty() ? "0" : ans;
    }
};
