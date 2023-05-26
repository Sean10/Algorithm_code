class Solution {
public:
    int removeDuplicates(vector<int>& nums) {
        if(nums.size() <= 2)
            return nums.size();
        int n = nums.size(), rear = 1;
        for(int i = 2;i < n; i++)
        {
            if(!(nums[i] == nums[rear] && nums[i] == nums[rear-1]))
                nums[++rear] = nums[i];
        }
        return rear+1;
    }
};
