class Solution {
public:
    bool isPerfectSquare(int num) {
        long long left = 0, right = num;
        while(left <= right)
        {
            long long temp_mid = (right+left)/2;
            if(temp_mid*temp_mid > num)
                right = temp_mid-1;
            else if(temp_mid*temp_mid < num)
                left = temp_mid+1;
            else
                return num%temp_mid == 0;
        }
        return false;
    }
};
