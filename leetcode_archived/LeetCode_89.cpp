class Solution {
public:
    vector<int> grayCode(int n) {
        vector<int> ans;
        bitset<32> temp;
        helper(temp ,ans, n);
        return ans;
    }

    void helper(bitset<32>& temp, vector<int>& ans, int n)
    {
        if(n == 0)
        {
            ans.push_back(temp.to_ulong());
            return ;
        }

        helper(temp, ans, n-1);
        temp.flip(n-1);
        helper(temp, ans, n-1);
    }
};
