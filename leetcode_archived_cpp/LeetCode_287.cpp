# two pointer

class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int slow = nums.size();
        int fast = slow;
        do
        {
            slow = nums[slow-1];
            fast = nums[nums[fast-1]-1];
        }while(slow != fast);

        fast = nums.size();
        while(slow != fast)
        {
            slow = nums[slow-1];
            fast = nums[fast-1];
        }
        return slow;
    }
};

# Binary

class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int left = 0, right = nums.size();
        while(left <= right)
        {
            int mid = (left + right)/2;
            int cnt = 0;
            for(auto n: nums)
                if(n <= mid)
                    cnt ++;
            if(cnt <= mid)
                left = mid + 1;
            else
                right = mid - 1;
        }
        return left;
    }
};
