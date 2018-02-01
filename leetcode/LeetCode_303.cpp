class NumArray {
public:
    NumArray(vector<int> nums):_nums(nums.size()+1, 0) {
        partial_sum(nums.begin(), nums.end(), _nums.begin()+1);

    }

    int sumRange(int i, int j) {
        return _nums[j+1] - _nums[i];

    }

    private:
    vector<int> _nums;
};

/**
 * Your NumArray object will be instantiated and called as such:
 * NumArray obj = new NumArray(nums);
 * int param_1 = obj.sumRange(i,j);
 */
