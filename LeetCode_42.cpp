class Solution {
public:
    int trap(vector<int>& height) {
        int n = height.size();
        if(n < 3)
            return 0;

        int left = 0, right = n-1, lower = 0, level = 0, water = 0;
        while(left < right)
        {
            lower = height[left] < height[right] ? height[left++] : height[right--];
            if(lower > level)
                level = lower;
            water += level - lower;
        }
        return water;
    }
};
