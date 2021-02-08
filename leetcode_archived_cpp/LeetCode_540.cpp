class Solution {
public:
    int singleNonDuplicate(vector<int>& nums) {
        int temp = 0;
        for (auto i: nums)
            temp ^= i;
        return temp;
    }
};
