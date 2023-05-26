class Solution {
public:
    vector<int> numberOfLines(vector<int>& widths, string S) {
        int lines = 1, nums = 0;
        for (auto c: S)
        {
            int width = widths[c-'a'];
            lines = nums + width > 100 ? lines+1 : lines;
            nums = nums + width > 100 ? width : nums + width;
        }
        return {lines, nums};
    }
};
