class Solution {
public:
    vector<int> searchRange(vector<int>& nums, int target) {
        auto bounds = equal_range(nums.begin(), nums.end(), target);
        if (bounds.first == bounds.second)
            return {-1, -1};
        return {bounds.first - nums.begin(), bounds.second - nums.begin() - 1};
    }
};

class Solution {
public:
    vector<int> searchRange(vector<int>& nums, int target) {
        int lo = lower_bound(nums.begin(), nums.end(), target) - nums.begin();
        if (lo == nums.size() || nums[lo] != target)
            return {-1, -1};
        int hi = upper_bound(nums.begin(), nums.end(), target) - nums.begin() - 1;
        return {lo, hi};
    }
};
