
// 这个算是2Pass的方法吧
class Solution {
public:

    int deleteAndEarn(vector<int>& nums) {
        vector<int> v(10001, 0);
        for(auto i:nums)
        {
            v[i] += i;
        }

        int take = 0, skip = 0;
        for (auto i :v)
        {
            int temp = max(skip+i, take);
            skip = take;
            take = temp;
        }
        return take;
    }
};

class Solution {
public:

    int deleteAndEarn(vector<int>& nums) {
        vector<int> v(10001, 0);
        for(auto i:nums)
        {
            v[i] ++;
        }

        vector<int> dp(v.size(), 0);
        dp[1] = v[1];
        for (int i = 2;i <= 10000; i++)
        {
            dp[i] = max(dp[i-1], v[i]*i+dp[i-2]);
        }
        return dp[10000];
    }
};

// 这是第一个想要直接排序用贪心方法，结果证明是错的，只有DP能够得到正确答案
struct cmp {
    bool operator()(const pair<int, int> &p1,const pair<int, int> &p2)
    {
        // return p1 > p2;
        return p1.first*p1.second > p2.first* p2.second;
    }
};

class Solution {
public:

    int deleteAndEarn(vector<int>& nums) {
        map<int, int> map_;
        unordered_map<int, bool> flag;
        for (auto i: nums)
        {
            map_[i] ++;
            flag[i] = true;
        }

        vector<pair<int, int>> v(map_.begin(), map_.end());
        sort(v.begin(), v.end(), cmp());



        int ans = 0;
        for (auto i = v.begin(); i != v.end(); i++)
        {
            if (!flag[i->first])
                continue;
            ans += i->first * i->second;
            if (flag[i->first-1])
                flag[i->first-1] = false;
            if (flag[i->first+1])
                flag[i->first+1] = false;
            // cout << i->first << " " << i->second << endl;
            // cout << ans;
        }

        return ans;
    }
};
