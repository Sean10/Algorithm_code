/*
// Employee info
class Employee {
public:
    // It's the unique ID of each node.
    // unique id of this employee
    int id;
    // the importance value of this employee
    int importance;
    // the id of direct subordinates
    vector<int> subordinates;
};
*/
class Solution {
private:
    void helper(unordered_map<int, Employee*> map_, int id, int& ans) {
        queue<int> q;
        for (int i = 0;i < map_[id]->subordinates.size(); i++)
            q.push(map_[id]->subordinates[i]);
        ans += map_[id]->importance;

        while (!q.empty()) {
            int temp_id = q.front();
            q.pop();

            ans += map_[temp_id]->importance;
            for (int i = 0;i < map_[temp_id]->subordinates.size(); i++)
                q.push(map_[temp_id]->subordinates[i]);

        }
    }

    public:

    int getImportance(vector<Employee*> employees, int id) {
        int ans = 0;
        unordered_map<int, Employee*> map_;
        for (auto i: employees)
            map_[i->id] = i;

        helper(map_, id, ans);
        return ans;
    }
};
