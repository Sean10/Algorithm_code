class Solution {
public:
    int findPeakElement(vector<int>& nums) {
        int left = 0, right = nums.size()-1;
        while(left < right)
        {
            int mid = (left + right)/2;
            if (nums[mid] > nums[mid+1])
                right = mid;
            else
                left = mid + 1;
        }
        return left;
    }
};


class Solution {
public:
    int findPeakElement(vector<int>& nums) {
        int i;
        nums.push_back(INT_MIN);
        nums.insert(nums.begin(), INT_MIN);
        for(i = 1; i < nums.size() -1; i++)
        {
            if(nums[i] > nums[i-1] && nums[i] > nums[i+1])
                return i-1;
        }
        if(nums[i-1] == INT_MIN)
            return i-2;
        return i-1;
    }
};
