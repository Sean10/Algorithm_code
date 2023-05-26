class Solution {
public:
    vector<int> findOrder(int numCourses, vector<pair<int, int>>& prerequisites) {
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
		vector<int> ans;
        while(!q.empty())
        {
            int temp = q.front();
            q.pop();

            cnt++;
			ans.push_back(temp);
            for(unordered_set<int>::iterator it = graph[temp].begin(); it != graph[temp].end(); it++)
            {
                degree[*it] -= 1;
                if(degree[*it] == 0)
                    q.push(*it);

            }
        }

        if(cnt < numCourses)
            return {};
		return ans;
    }
};


# DFS

class Solution {
public:
    vector<int> findOrder(int numCourses, vector<pair<int, int>>& prerequisites) {
        vector<unordered_set<int>> graph(numCourses);
        vector<int> degree(numCourses, 0);
        for(auto pre: prerequisites)
        {
            degree[pre.first] += 1;
            graph[pre.second].insert(pre.first);
        }

        vector<int> ans;
        int cnt = 0;
        for(int i = 0;i < numCourses; i++)
        {
            if(degree[i] == 0 && !DFS(ans, graph, degree, i,cnt))
            {
                return {};
            }

        }
        cout << cnt << endl;

        if(cnt < numCourses)
            return {};
        return ans;
    }

    bool DFS(vector<int> &ans, vector<unordered_set<int>>& graph, vector<int> &degree, int i,int& cnt)
    {
        if(degree[i])
        {
            cout << degree[i] << endl;
            return false;
        }
        if(degree[i] == 0)
        {
            ans.push_back(i);
            degree[i] --;

        }
        cnt++;
        for(unordered_set<int>::iterator it = graph[i].begin(); it != graph[i].end(); it++)
        {
            degree[*it] --;
            if(degree[*it] == 0 && !DFS(ans, graph, degree, *it, cnt))
            {
                cout << *it << "\t" << degree[*it] << endl;
                return false;
            }
        }
        return true;
    }
};
