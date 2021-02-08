class Solution {
public:
    vector<int> dailyTemperatures(vector<int>& temperatures) {
        int n = temperatures.size();
        vector<int> ans(n, 0);
        stack<pair<int, int>> s;
        for (int i = 0;i < n; i++)
        {
            while (!s.empty() && s.top().first < temperatures[i])
            {
                ans[s.top().second] = i - s.top().second;
                s.pop();
            }
            s.push(make_pair(temperatures[i], i));
        }
        return ans;
    }

};

class Solution {
public:
    vector<int> dailyTemperatures(vector<int>& temperatures) {
        int n = temperatures.size();
        vector<int> ans(n, 0);
        vector<int> next(101, INT_MAX);
        for (int i = temperatures.size()-1;i >= 0; i--)
        {
            int earlist= INT_MAX;
            for (int j = temperatures[i]+1; j <= 100; j++)
                earlist = min(earlist, next[j]);
            if (earlist != INT_MAX)
                ans[i] = earlist - i;
            next[temperatures[i]] = i;

        }
        return ans;
    }

};


// TLE
class Solution {
public:
    vector<int> dailyTemperatures(vector<int>& temperatures) {
        vector<int> ans(temperatures.size(), 0);
        for (int i = 0;i < temperatures.size(); i++)
        {
            int j = i+1;
            while(j < temperatures.size() && temperatures[j] <= temperatures[i])
                j++;
            ans[i] = j == temperatures.size() ? 0 : j-i;
        }
        return ans;
    }

};
