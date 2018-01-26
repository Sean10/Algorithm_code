class Solution {
public:
    vector<vector<string>> groupAnagrams(vector<string>& strs) {
        unordered_map<string, vector<string>> map_;
        for(auto i: strs)
        {
            string temp = i;
            sort(temp.begin(), temp.end());
            map_[temp].push_back(i);
        }

        vector<vector<string>> ans;
        for(auto i: map_)
        {
            sort(i.second.begin(), i.second.end());
            ans.push_back(i.second);
        }
        return ans;
    }
};
