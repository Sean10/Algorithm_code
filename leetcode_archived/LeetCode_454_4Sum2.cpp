class Solution {
public:
    int fourSumCount(vector<int>& A, vector<int>& B, vector<int>& C, vector<int>& D) {
        int ans = 0;
        int n = A.size();
        unordered_map<int,int> setAB;
        for(auto i:A)
            for (auto j:B)
                ++setAB[i+j];

        for(auto i:C)
            for(auto j:D)
            {
                auto it = setAB.find(0-i-j);
                if(it != setAB.end())
                    ans += it->second;
            }


        return ans;
    }


};


// TLE
//
class Solution {
public:
    int fourSumCount(vector<int>& A, vector<int>& B, vector<int>& C, vector<int>& D) {
        int ans = 0;
        int n = A.size();
        qsort(A, 0, n-1);
        qsort(B, 0, n-1);
        qsort(C, 0, n-1);
        qsort(D, 0, n-1);
        A.push_back(LLONG_MIN);
        B.push_back(LLONG_MIN);
        C.push_back(LLONG_MIN);
        D.push_back(LLONG_MIN);

        for(int i = 0;i <= n; i++)
        {
            if (A[i] == A[i+1] || A[i] == LLONG_MIN || A[i]+B[n-1]+C[n-1]+D[n-1] < 0 ||  A[i]+B[0]+C[0]+D[0] > 0)
                continue;
            for(int j = 0; j <= n;j++)
            {
                if (B[j] == B[j+1] || B[j] == LLONG_MIN ||  A[i]+B[j]+C[n-1]+D[n-1] < 0 ||  A[i]+B[j]+C[0]+D[0] > 0)
                    continue;
                for(int k = 0;k <= n;k++)
                {
                    if(C[k] == C[k+1] || C[k] == LLONG_MIN || A[i]+B[j]+C[k]+D[n-1] < 0 ||  A[i]+B[j]+C[k]+D[0] > 0)
                        continue;

                    if(A[i]+B[j]+C[k]+D[n-1] < 0)
                        continue;
                    int left = 0, right = n-1;
                    while(left < right)
                    {
                        int mid = left + (right-left)/2;
                        if(A[i]+B[j]+C[k]+D[mid] == 0)
                            ans++;
                        else if(A[i] + B[j] +C[k] +D[mid] < 0)
                            left = mid+1;
                        else
                            right = mid;
                    }
                }
            }
        }
        return ans;
    }

    void qsort(vector<int>& A, int left, int right)
    {
        if(left >= right)
            return ;
        int mid = partition(A, left, right);
        qsort(A, left, mid-1);
        qsort(A, mid+1, right);
    }

    int partition(vector<int>& A, int left, int right)
    {
        int temp = A[left];
        while(left < right)
        {
            while(left < right && A[right] > temp)
                right--;
            if(left < right)
                A[left] = A[right--];
            while(left < right && A[left] < temp)
                left++;
            if(left < right)
                A[right] = A[left++];
        }
        A[left] = temp;
        return left;
    }
};
