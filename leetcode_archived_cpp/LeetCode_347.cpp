class Solution {


public:
    struct CmpByValue {
        bool operator()(const pair<int,int> & lhs, const pair<int,int> & rhs)
        {
            return lhs.second > rhs.second;
        }
    };

    vector<int> topKFrequent(vector<int>& nums, int k) {
        map<int, int> map_;
        for(int num: nums)
            map_[num]++;

        vector<int> ans;
        vector<pair<int, int>> temp(map_.begin(), map_.end());
        sort(temp.begin(), temp.end(), CmpByValue());
        for(int i = 0;i < k; i++)
            ans.push_back(temp[i].first);
        return ans;

    }
};
