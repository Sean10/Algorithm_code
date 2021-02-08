// Forward declaration of isBadVersion API.
bool isBadVersion(int version);

class Solution {
public:
    int firstBadVersion(int n) {
        int left = 0, right = n;
        while(left < right)
        {
            int mid = left + (right-left)/2;
            bool check = isBadVersion(mid);
            if(check)
                right = mid;
            else
                left = mid + 1;
        }
        return left;
    }
};
