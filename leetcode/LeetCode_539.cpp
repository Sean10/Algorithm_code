class Solution {
public:
    int findMinDifference(vector<string>& timePoints) {
        int n = timePoints.size();
        sort(timePoints.begin(), timePoints.end());

        int min_diff = INT_MAX;
        for (int i = 0;i < n; i++)
        {
            int diff = abs(timediff(timePoints[(i-1+n)%n], timePoints[i]));
            diff = min(diff, 1440 - diff);
            min_diff = min(min_diff, diff);
        }

        return min_diff;
    }

private:
    int timediff(string t1, string t2)
    {
        int h1 = stoi(t1.substr(0, 2));
        int h2 = stoi(t2.substr(0, 2));
        int m1 = stoi(t1.substr(3, 2));
        int m2 = stoi(t2.substr(3, 2));
        return (h1 - h2)*60 + (m1 - m2);
    }
};
