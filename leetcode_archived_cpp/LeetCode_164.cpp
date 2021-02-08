class Solution {
public:
    int maximumGap(vector<int>& nums) {
        int n = nums.size();
        if (n < 2)
            return 0;

        int maxV = *max_element(nums.begin(), nums.end());
        int minV = *min_element(nums.begin(), nums.end());
        int size = max(1, (maxV - minV)/(n - 1));
        int length = (maxV - minV)/size + 1;
        vector<int> bucket_max(length, INT_MIN);
        vector<int> bucket_min(length, INT_MAX);


        for (int i = 0; i < n; i++)
        {
            int index = (nums[i] - minV) / size;
            bucket_max[index] = max(bucket_max[index], nums[i]);
            bucket_min[index] = min(bucket_min[index], nums[i]);
        }


        int gap_max = 0, last_max = bucket_max[0];
        for (int i = 1;i < length; i++)
        {
            if (bucket_max[i] == INT_MIN)
                continue;
            gap_max = max(gap_max, bucket_min[i] - last_max);
            last_max = bucket_max[i];
        }
        return gap_max;
    }
};

class Solution {
public:
    int maximumGap(vector<int>& nums) {
        if (nums.size() < 2)
            return 0;
        sort(nums.begin(), nums.end());
        int max_ = INT_MIN;
        for (int i = 1; i < nums.size(); i++)
            max_ = max(max_, nums[i] - nums[i-1]);
        return max_;
    }
};
