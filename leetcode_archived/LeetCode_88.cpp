class Solution {
public:
    void merge(vector<int>& nums1, int m, vector<int>& nums2, int n) {
        if(n == 0 || m > nums1.size() || n > nums2.size())
            return ;
        int i = m-1;
        int j = n-1;
        int k = m+n-1;
        while(i >= 0 && j >= 0)
            nums1[k--] = nums1[i] > nums2[j] ? nums1[i--] : nums2[j--];
        while(k >= 0)
            nums1[k--] = i >= 0 ? nums1[i--] : nums2[j--];
    }
};
