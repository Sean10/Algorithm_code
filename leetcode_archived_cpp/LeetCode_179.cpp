class Solution {
public:
    string largestNumber(vector<int>& nums) {
        vector<string> v_str;
        for(int i: nums)
            v_str.push_back(to_string(i));

        sort(v_str.begin(), v_str.end(), [](string a, string b){return a+b>b+a;});

        string ans;
        for(string i: v_str)
            ans += i;
        while(ans[0] == '0' && ans.size() > 1)
            ans.erase(0,1);
        return ans;

    }
};
