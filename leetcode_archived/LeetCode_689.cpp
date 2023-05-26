class Solution {
public:
    vector<int> maxSumOfThreeSubarrays(vector<int>& nums, int k) {
        int n = nums.size();
        vector<int> sum = {0}, posLeft(n, 0), posRight(n, n-k);
        
        for (auto i: nums)
            sum.push_back(sum.back()+i);
        
        for (int i = 1, total = sum[k] - sum[0]; i < n-k;i ++)
        {
            if (sum[i+k] - sum[i] > total)
            {
                posLeft[i] = i;
                total = sum[i+k] - sum[i];
            }else
                posLeft[i] = posLeft[i-1];
        }
        
        for (int i = n-k-1, total = sum[n] - sum[n-k]; i >= 0; i--)
        {
            if (sum[i+k] - sum[i] >= total)
            {
                posRight[i] = i;
                total = sum[i+k] - sum[i];
            }else
                posRight[i] = posRight[i+1];
        }
        
        vector<int> ans;
        int max_ = 0;
        for (int i = k; i <= n-2*k; i++)
        {
            int l = posLeft[i-k], r = posRight[i+k];
            int total = sum[l+k] - sum[l]+ sum[i+k] - sum[i] + sum[r+k] - sum[r];
            if (total > max_)
            {
                max_ = total;
                ans = {l, i, r};
            }
        }
        return ans;
    }
};
