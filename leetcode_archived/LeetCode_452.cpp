class Solution {
public:
    int findMinArrowShots(vector<pair<int, int>>& points) {
        int cnt = 0, arrow = INT_MIN;
        sort(points.begin(), points.end(), [](const pair<int, int>& a, const pair<int, int>& b){ return a.second==b.second ? a.first < b.first : a.second < b.second;});
        for (auto i: points)
        {
            if (arrow != INT_MIN && i.first <= arrow)
                continue;
            arrow = i.second;
            cnt++;
        }

        return cnt;
    }
};
