class Solution {
public:
    string minWindow(string s, string t) {
        vector<int> map_(128, 0);
        for (auto i: t)
            map_[i] ++;

        int count = t.size(), begin = 0, end = 0, head = 0, d = INT_MAX;
        while (end < s.size())
        {
            if (map_[s[end++]]-- > 0)
                count--;
            while(count == 0)
            {
                if (end - begin < d)
                    d = end - (head = begin);
                if(map_[s[begin++]]++ == 0)
                    count ++;
            }
        }
        return d == INT_MAX ? "" : s.substr(head, d);

    }
};
