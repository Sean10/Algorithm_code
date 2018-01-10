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
    vector<Interval> merge(vector<Interval>& intervals) {
        if(intervals.empty())
            return vector<Interval>{};

        vector<Interval> ans;

        sort(intervals.begin(), intervals.end(), [](Interval a, Interval b){return a.start < b.start;});

        ans.push_back(intervals[0]);
        for(int i = 1;i < intervals.size(); i++)
        {
            if (ans.back().end < intervals[i].start)
                ans.push_back(intervals[i]);
            else
                ans.back().end = max(ans.back().end, intervals[i].end);
        }
        return ans;

    }
};
