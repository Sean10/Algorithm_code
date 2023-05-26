class Solution {
public:
    int leastInterval(vector<char>& tasks, int n) {
        vector<int> v(256, 0);

        int count = 0;
        for (auto task: tasks)
        {
            v[task] ++;
            count = max(count, v[task]);
        }

        int ans = (count-1)*(n+1);
        for (int i = 0;i < 256;i++)
        {
            if (v[i] == count)
                ans++;
        }
        return max(ans, (int)tasks.size());


    }
};
