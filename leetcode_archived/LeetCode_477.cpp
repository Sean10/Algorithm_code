class Solution {
public:
    int totalHammingDistance(vector<int>& nums) {
        if (nums.size() <= 0)
            return 0;

        int ans = 0;

        for (int i = 0;i < 32; i++)
        {
            int zeroCount = 0;

            for (auto n: nums)
            {
                if ((n & (1 << i)) == 0)
                    zeroCount ++;
            }
            ans += zeroCount*(nums.size() - zeroCount);
        }

        return ans;
    }
};
