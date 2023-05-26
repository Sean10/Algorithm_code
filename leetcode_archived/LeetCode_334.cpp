class Solution {
public:
    bool increasingTriplet(vector<int>& nums) {
        int x1 = INT_MAX, x2 = INT_MAX;
        for (int i: nums)
        {
            if (i <= x1)
                x1 = i;
            else if (i <= x2)
                x2 = i;
            else
                return true;
        }
        return false;
    }
};
