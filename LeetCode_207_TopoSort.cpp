class Solution {
public:
    bool canFinish(int numCourses, vector<pair<int, int>>& prerequisites) {
        vector<unordered_set<int>> graph(numCourses);
        vector<int> degree(numCourses, 0);
        for(auto pre: prerequisites)
        {
            degree[pre.first] += 1;
            graph[pre.second].insert(pre.first);
        }

        queue<int> q;
        for(int i = 0;i < numCourses; i++)
        {
            if(degree[i] == 0)
                q.push(i);
        }

        int cnt = 0;
        while(!q.empty())
        {
            int temp = q.front();
            q.pop();

            cnt++;
            for(unordered_set<int>::iterator it = graph[temp].begin(); it != graph[temp].end(); it++)
            {
                degree[*it] -= 1;
                if(degree[*it] == 0)
                    q.push(*it);

            }
        }

        if(cnt < numCourses)
            return false;
        return true;

    }
};
