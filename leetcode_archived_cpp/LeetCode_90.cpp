class Solution {
public:
    vector<vector<int>> subsetsWithDup(vector<int>& nums) {
        set<vector<int>> temp;
        //sort(nums.begin(), nums.end());
        qsort(nums, 0, nums.size()-1);
        helper(nums, {}, temp, 0);
        vector<vector<int>> ans;
        ans.assign(temp.begin(), temp.end());
        return ans;
    }

    void helper(vector<int>& nums, vector<int> temp, set<vector<int>>& ans, int start)
    {
        ans.insert(temp);

        for(int i = start;i < nums.size(); i++)
        {
            temp.push_back(nums[i]);
            helper(nums, temp, ans, i+1);
            temp.pop_back();
        }
    }

    void qsort(vector<int>& nums, int left, int right)
    {
        if(left > right)
            return ;
        int mid = partition(nums,left, right);
        qsort(nums, left, mid-1);
        qsort(nums, mid+1, right);
    }

    int partition(vector<int>& nums, int left, int right)
    {
        int temp = nums[left];
        while(left < right)
        {
            while(left < right && temp < nums[right])
                right --;
            if(left < right)
                nums[left++] = nums[right];

            while(left < right && temp > nums[left])
                left ++;
            if(left < right)
                nums[right--] = nums[left];
        }
        nums[left] = temp;
        return left;
    }
};
