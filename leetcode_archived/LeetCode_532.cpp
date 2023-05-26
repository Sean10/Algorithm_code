class Solution {
public:
    int findPairs(vector<int>& nums, int k) {
        sort(nums.begin(), nums.end());
        set<pair<int, int>> set_;
        int ans = 0;
        for(int i = 0;i < nums.size(); i++)
        {
            for(int j = i+1; j < nums.size() && abs(nums[j] - nums[i]) <= k; j++)
            {
                if(abs(nums[j]-nums[i]) == k && set_.find(make_pair(nums[i],nums[j])) == set_.end())
                    ans += 1;
                    set_.insert(make_pair(nums[i],nums[j]));
                    //cout << nums[i] << nums[j];
            }
        }
        return ans;
    }
};


class Solution {
public:
    int findPairs(vector<int>& nums, int k) {
        if(k < 0)
            return 0;
        sort(nums.begin(), nums.end());
        map<int,int> map_;
        for(int i = 0;i < nums.size(); i++)
        {
            map_[nums[i]] = i;
        }
        int ans = 0;
        for(int i = 0; i < nums.size(); i++)
        {
            if(map_.find(nums[i]+k) != map_.end() && (map_.at(nums[i]+k) != i))
            {
                ans += 1;
                map_.erase(nums[i]+k);
            }
        }
        return ans;
    }
};
