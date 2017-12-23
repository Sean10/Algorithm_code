class Solution {
public:
    int partition(vector<int>& nums, int left, int right)
    {
        int i = left, j = right;
        int temp = nums[left];
        while(i < j)
        {
            while(i < j && temp < nums[j])
                j--;
            if(i < j)
                nums[i++] = nums[j];

            while(i < j && temp > nums[i])
                i++;
            if(i < j)
                nums[j--] = nums[i];
        }

        nums[i] = temp;
        return i;
    }

    void quicksort(vector<int>& nums, int left, int right)
    {
        if(left >= right)
            return ;
        int j = partition(nums, left, right);
        quicksort(nums,left, j-1);
        quicksort(nums, j+1, right);
    }

    int findKthLargest(vector<int>& nums, int k) {
        quicksort(nums,0,nums.size()-1);
        return nums[nums.size()-k];
    }
};
