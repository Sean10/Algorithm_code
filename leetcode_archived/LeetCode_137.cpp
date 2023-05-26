class Solution {
public:
    int singleNumber(vector<int>& nums) {
        int ones = 0, twos = 0;
        for (auto i: nums)
        {
            ones = (ones ^ i) & ~ twos;
            twos = (twos ^ i) & ~ ones;
        }
        return ones;
    }
};

class Solution {
public:
    int singleNumber(vector<int>& nums) {
        int one = 0, two = 0, three = 0;
        for(auto i :nums)
        {
            two |= (i&one);
            one ^= i;
            three = ~(one&two);
            one &= three;
            two &= three;
        }
        return one;
    }
};


class Solution {
public:
    int singleNumber(vector<int>& nums) {

        int ans = 0;

        for (int i = 0;i < 32; i++)
        {
            int bit = 1 << i;
            int cnt = 0;
            for (auto i: nums)
            {
                if(bit&i)
                    cnt ++;
            }

            if (cnt%3 != 0)
                ans |= bit;
        }

        return ans;
    }
};
