class Solution {
public:
    bool canTransform(string start, string end) {
        int n = start.size(), i = 0, j = 0;
        string s1, s2;

        while (i < n && j < n)
        {
            while (start[i] == 'X') i++;
            while (end[j] == 'X') j++;
            if (i == n && j == n)
                break;
            if (i == n || j == n || start[i] != end[j])
                return false;
            if (start[i] == 'R' && i > j || start[i] == 'L' && i < j)
                return false;
            else
            {
                if (start[i] != 'X')
                    s1 += start[i++];
                if (end[j] != 'X')
                    s2 += end[j++];
            }

            // cout << s1 << endl;
            // cout << s2 << endl;
        }

        return s1 == s2;

    }
};
