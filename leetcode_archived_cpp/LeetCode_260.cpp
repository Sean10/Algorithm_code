class Solution {
public:
    vector<int> singleNumber(vector<int>& nums) {
        int xorb = 0;
        for(auto i: nums)
            xorb ^= i;
        int rightmost = xorb & ~(xorb - 1);
        int a = 0, b = 0;
        for (auto i: nums)
        {
            if (i&rightmost)
                a ^= i;
            else
                b ^= i;
        }
        return {a, b};
    }
};
