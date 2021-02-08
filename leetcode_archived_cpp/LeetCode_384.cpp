class Solution {
public:
    Solution(vector<int> nums):nums(nums), temp(nums) {
        // set<int> nums_set;
        srand(time(NULL));
        // for (auto i: nums)
        //     nums_set.insert(i);
        // this->nums.assign(nums_set.begin(), nums_set.end());

    }

    /** Resets the array to its original configuration and return it. */
    vector<int> reset() {
        return this->temp;
    }

    /** Returns a random shuffling of the array. */
    vector<int> shuffle() {
        // vector<int> nums = this->nums;
        for (int i = this->nums.size()-1;i >= 0; i--)
        {
            int j = rand()%(i+1);
            swap(this->nums[i], this->nums[j]);
        }
        return this->nums;
    }

    private:
    vector<int> nums;
    vector<int> temp;
};

/**
 * Your Solution object will be instantiated and called as such:
 * Solution obj = new Solution(nums);
 * vector<int> param_1 = obj.reset();
 * vector<int> param_2 = obj.shuffle();
 */
