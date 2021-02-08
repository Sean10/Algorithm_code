class Solution {
public:
    int splitArray(vector<int>& nums, int m) {
        int max_ = INT_MIN;
        long sum = 0;
        for (auto num: nums)
        {
            max_ = max(num, max_);
            sum += num;
        }
        return binarySearch(nums, m, max_, sum);
    }
    
    int binarySearch(vector<int>& nums, int m, int low, long high) {
        while (low < high){
            long mid = (low + high) /2;
            if (isValid(nums, m, mid))
                high = mid;
            else
                low = mid + 1;
        }
        return low;
    }
    
    bool isValid(vector<int>& nums, int m, long mid) {
        long curr = 0;
        int count = 1;
        for (auto num: nums) {
            curr += num;
            if (curr > mid) {
                curr = num;
                count ++;
                
                if (count > m)
                    return false;
            }
        }
        return true;
    }
};
