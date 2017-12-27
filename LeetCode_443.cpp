class Solution {
public:
    int compress(vector<char>& chars) {
        int n = chars.size();
        if(n < 2)
            return n;

        int cnt = 1, ans = 0;
        for(int i = 1;i <= n;i ++)
        {
            if(i == n || chars[i] != chars[i-1])
            {
                chars[ans++] = chars[i-1];
                if(cnt == 1)
                    continue;
                string temp = to_string(cnt);
                for(int i = 0;i < temp.size(); i++)
                    chars[ans++] = temp[i];
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
