class Solution {
public:
    int search(vector<int>& nums, int target) {
        int low = 0, high = nums.size();
        while(low < high)
        {
            int mid = (low+high)/2;
            int num;
            if(nums[mid] < nums[0] == nums[0] > target)
                num = nums[mid];
            else
                num = target < nums[0] ? INT_MIN : INT_MAX;

            if(num < target)
                low = mid + 1;
            else if(num > target)
                high = mid;
            else
                return mid;
        }

        return -1;
    }
};
