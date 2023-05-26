class Solution {
public:
    vector<int> nextGreaterElements(vector<int>& nums) {
        vector<int> saved(nums.begin(), nums.end());
        // cout << nums.size()-1 << endl;
        
        for (int i = 0;i < (int)nums.size()-1; i++)
            saved.push_back(nums[i]);

        // cout << eee << endl;
        
        stack<int> s;
        unordered_map<int, queue<int>> map_;
        
        for (int i = 0;i < saved.size(); i++)
        {
            while(s.size() && s.top() < saved[i])
            {
                map_[s.top()].push(saved[i]);
                s.pop();
            }
            if (i < nums.size())
                s.push(saved[i]);
        }
        
        vector<int> ans;
        for (auto i: nums)
        {
            ans.push_back(map_.count(i) ? map_[i].front() : -1);
            if (map_.count(i))
                map_[i].pop();
        }
        return ans;
    }
};
