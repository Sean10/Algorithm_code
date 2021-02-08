class Solution {
public:
    string countAndSay(int n) {
        if(n == 1)
            return "1";
        string temp = countAndSay(n-1);

        int cnt = 1;
        string ans = "";
        for(int i = 1;i <= temp.size(); i++)
        {
            if(i == temp.size() || temp[i] != temp[i-1])
            {
                ans = ans+to_string(cnt)+temp[i-1];
                cnt = 1;
            }
            else
            {
                cnt++;
            }
        }
        return ans;
    }
};
