class Solution {
    public:
    struct Node {
        int val;
        int i;
        int j;

        Node (int _val, int _i, int _j): val(_val), i(_i), j(_j) {}
    };

    struct cmp {
        bool operator()(const Node A, const Node B) {
            return A.val > B.val;
        }
    };

    vector<int> smallestRange(vector<vector<int>>& nums) {
        priority_queue<Node, vector<Node>, cmp> pq;
        int cur_min = INT_MAX, cur_max = INT_MIN, cur_range = INT_MAX;

        int start, end;

        for (int i = 0;i < nums.size(); i++)
        {
            Node temp(nums[i][0], i, 0);
            pq.push(temp);
            cur_max = max(cur_max, nums[i][0]);
            // cur_min = min(cur_min, nums[i][0]);
        }

        while (true)
        {
            auto top = pq.top();
            pq.pop();
            cur_min = top.val;
            if (cur_max - cur_min < cur_range)
            {
                start = cur_min;
                end = cur_max;
                cur_range = end - start;
            }

            if ((top.j + 1) == nums[top.i].size())
                break;
            Node next(nums[top.i][top.j+1], top.i, top.j+1);
            pq.push(next);
            if (next.val > cur_max)
                cur_max = next.val;
        }
        return {start, end};
    }
};
