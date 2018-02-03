class Solution {
public:
    vector<vector<string>> findDuplicate(vector<string>& paths) {
        unordered_map<string, vector<string>> map_;

        for (auto i: paths)
        {
            stringstream ss(i);
            string root, s;
            getline(ss, root, ' ');
            while(getline(ss, s, ' '))
            {
                string filename = root + '/' + s.substr(0, s.find('('));
                string filecontent = s.substr(s.find('(')+1, s.find(')') - s.find('(')-1);
                map_[filecontent].push_back(filename);
            }
        }

        vector<vector<string>> ans;
        for (auto i: map_)
            if (i.second.size() > 1)
                ans.push_back(i.second);
        return ans;
    }
};
