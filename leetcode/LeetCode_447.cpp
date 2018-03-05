class Solution {
public:
    int numberOfBoomerangs(vector<pair<int, int>>& points) {
        int boom = 0;
        for (auto i: points)
        {
            unordered_map<double, int> map_;
            for (auto j: points)
                boom += 2*map_[hypot(i.first-j.first, i.second - j.second)]++;
        }
        return boom;
    }
};
