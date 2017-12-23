class Solution {
public:
    void rotate(vector<int>& nums, int k) {
        int n = nums.size();
        if(n < 0 || k%n == 0)
            return ;

        k = (k+n)%n;
        cout << k;
        int rotated = 0;
        int s = 0;
        while(rotated < n)
        {
            int j = s;
            int start = s,curr = nums[s];
            s++;
            do
            {
                int temp = nums[(j+k)%n];
                nums[(j+k)%n] = curr;
                curr = temp;
                j = (j+k)%n;
                rotated++;
            }while(start != j);
        }
    }
};
