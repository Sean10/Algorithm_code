/**
 * Definition for an interval.
 * struct Interval {
 *     int start;
 *     int end;
 *     Interval() : start(0), end(0) {}
 *     Interval(int s, int e) : start(s), end(e) {}
 * };
 */
class Solution {
public:
    vector<int> findRightInterval(vector<Interval>& intervals) {
        map<int, int> map_;
        for (auto i = 0;i < intervals.size(); i++)
            map_[intervals[i].start] = i;

        vector<int> ans;
        for (auto i: intervals)
        {
            auto temp = map_.lower_bound(i.end);
            if (temp == map_.end())
                ans.push_back(-1);
            else
                ans.push_back(temp->second);
        }
        return ans;

    }
};
