// DP
class Solution {
public:
    bool canPartition(vector<int>& nums) {
        int sum = accumulate(nums.begin(), nums.end(), 0);
        return sum&1 ? 0 : subset(nums, sum >> 1);
    }

    int subset(vector<int>& nums, int sum)
    {
        vector<int> dp(sum+1, 0);
        dp[0] = 1;
        for (auto n: nums)
        {
            for (int i = sum; i >= n; i--)
                dp[i] += dp[i-n];
        }
        // cout << dp[sum];
        return dp[sum];
    }
};


// bitset
class Solution {
public:
    bool canPartition(vector<int>& nums) {
        bitset<10001> bit(1);
        int sum = accumulate(nums.begin(), nums.end(), 0);
        for (auto i: nums)
            bit |= bit << i;
        return sum%2 == 0 && bit[sum >> 1];
    }
};


// DFS
class Solution {
public:
    bool canPartition(vector<int>& nums) {
        int sum = accumulate(nums.begin(), nums.end(), 0);
        sort(nums.begin(), nums.end(), [](int l1, int l2){return l1 > l2;});
        return sum%2 == 0 && dfs(nums, 0, sum >> 1, sum);
    }

private:
    bool dfs(vector<int>& nums, int start, int target, int left)
    {
        for (int i = start; i < nums.size(); i++)
        {
            left -= nums[i];

            if (nums[i] > target)
                continue;
            if (nums[i] == target || left == target)
                return true;
            if (dfs(nums, i+1, target - nums[i], left))
                return true;

            if (left < target)
                return false;
        }
        return false;
    }
};
