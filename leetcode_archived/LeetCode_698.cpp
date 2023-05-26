// dfs
class Solution {
public:
    bool ans;
    bool canPartitionKSubsets(vector<int>& nums, int k) {
        int sum = accumulate(nums.begin(), nums.end(), 0);
        sort(nums.begin(), nums.end(), [](int a, int b){return a>b;});
        if (sum%k != 0)
            return false;
        vector<int> bucket(k, 0);
        ans = false;
        dfs(nums, 0, sum/k, bucket);
        return  ans;

    }

private:
    void dfs(vector<int>& nums, int pos, int target, vector<int> bucket)
    {
        if (ans)
            return ;
        if (pos >= nums.size())
        {
            ans = true;
            return ;
        }

        bool flag = false;
        for (int i = 0; i < bucket.size(); i++)
        {
            if (flag && bucket[i] == 0)
                continue;

            if (bucket[i] == 0)
                flag = true;
            if (bucket[i] + nums[pos] > target)
                continue;
            bucket[i] += nums[pos];
            dfs(nums, pos+1, target, bucket);
            bucket[i] -= nums[pos];
        }
    }
};


// error code
class Solution {
public:
    bool canPartitionKSubsets(vector<int>& nums, int k) {
        int sum = accumulate(nums.begin(), nums.end(), 0);
        sort(nums.begin(), nums.end(), [](int a, int b){return a>b;});
        int cnt = 0;
        dfs(nums, 0, sum/k, sum, cnt);
        cout << cnt << endl;
        return sum%k == 0 && cnt == k;

    }

private:
    void dfs(vector<int>& nums, int start, int target, int left, int& cnt)
    {
        for (int i = start; i < nums.size(); i++)
        {
            left -= nums[i];

            if (nums[i] > target)
                continue;

            if (nums[i] == target || left == target)
            {
                cnt ++;
                return ;
            }

            dfs(nums, i+1, target-nums[i], target, cnt);

            if (left < target)
                return ;
        }
    }
};
