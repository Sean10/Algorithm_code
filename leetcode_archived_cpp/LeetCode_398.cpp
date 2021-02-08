class Solution {
public:
    Solution(vector<int> nums):_nums(nums) {
        // srand(NULL);
    }

    int pick(int target) {
        int n = 0, ans = 1;
        for (int i = 0;i < _nums.size(); i++)
        {
            if (_nums[i] != target)
                continue;
            if (n == 0)
            {
                ans = i;
                n++;
            }
            else
            {
                n++;
                if (rand() %n == 0)
                    ans = i;
            }
        }
        return ans;
    }

private:
    vector<int> _nums;
};

/**
 * Your Solution object will be instantiated and called as such:
 * Solution obj = new Solution(nums);
 * int param_1 = obj.pick(target);
 */
