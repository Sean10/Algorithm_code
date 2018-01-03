class Solution {
public:
    vector<vector<int>> subsets(vector<int>& nums) {
        vector<vector<int>> ans;
        //qsort(nums, 0, nums.size()-1);
        //sort(nums.begin(), nums.end());
        helper(nums, {}, ans, 0);
        return ans;
    }

    void helper(vector<int>& nums, set<int> temp, vector<vector<int>>& ans, int start)
    {
        vector<int> t;
        t.assign(temp.begin(), temp.end());
        ans.push_back(t);

        for(int i = start; i < nums.size(); i++)
        {
            temp.insert(nums[i]);
            helper(nums, temp, ans, i+1);
            temp.erase(nums[i]);
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
