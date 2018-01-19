class Solution {
public:
    vector<int> plusOne(vector<int>& digits) {
        if (digits.size() < 1)
            return {1};
        // int temp = digits[digits.size()-1];
        int carry = 1;
        int n = digits.size();
        // digits[n-1] = 1;
        vector<int> ans;
        // cout << ans[0];

        for(int i = n-1; i >= 0;i--)
        {
            int temp = digits[i] + carry;
            ans.insert(ans.begin(),1, temp%10);
            carry = temp/10;
            // cout << temp;
        }
        // cout << ans[0];
        if (carry != 0)
            ans.insert(ans.begin(),1, carry);
        return ans;
    }
};
