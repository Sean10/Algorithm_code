class Solution {
public:
    bool isIdealPermutation(vector<int>& A) {
        for(int i = 0;i < A.size(); i++)
        {
            if(abs(A[i]-i) > 1)
                return false;
        }
        return true;
    }
};


//TLE
class Solution {
public:
    bool isIdealPermutation(vector<int>& A) {
        int N = A.size();
        int cnt_global = 0, cnt_local = 0;
        // vector<int> flag(N, 0);
        for(int i = 0;i < N; i++)
        {
            for(int j = i+1;j < N;j++)
            {
                if(A[i] >A[j])
                    cnt_global++;
            }
            if(i < N-1 && A[i] > A[i+1])
                cnt_local++;
        }
        //cout << cnt_global << cnt_local << endl;
        return cnt_global == cnt_local;
    }
};

//还有bug的使用归并排序寻找逆序对
class Solution {
public:
    bool isIdealPermutation(vector<int>& A) {
        int N = A.size();
        int cnt_global = 0, cnt_local = 0;
        vector<int> flag(N, 0);
        for(int i = 0;i < N; i++)
        {
            if(i < N-1 && A[i] > A[i+1])
                cnt_local++;



            int temp = A[i];
            int x = i, y = i;
            while(x > 0 && temp < A[--x])
            {
                A[y--] = A[x];
                // cout << "xx";
            }
            A[y] = temp;

            // cout << cnt_global << endl;
        }
        cnt_global = countInversion(A,0,N-1);
        cout << cnt_global << cnt_local << endl;
        return cnt_global == cnt_local;
    }


    int countInversion(vector<int>& A, int p, int r)
    {
        int inversion = 0;
        if(p < r)
        {
            int q = (p+r)/2;
            inversion += countInversion(A, p, q);
            inversion += countInversion(A, q+1, r);
            inversion += mergeInversion(A, p, q, r);
        }
        return inversion;
    }

    int mergeInversion(vector<int>& A, int p, int q, int r)
    {
        int n1 = q-p+1, n2 = r-q;
        vector<int> L(n1+2, 0), R(n2+2, 0);
        for(int i = 1;i <= n1;i++)
            L[i] = A[p+i-1];
        for(int i = 1;i <= n2; i++)
            R[i] = A[q+i];
        L[n1+1] = INT_MAX;
        R[n2+1] = INT_MAX;

        int inversion = 0;
        bool counted = false;

        for(int k = p,i = 1, j = 1;k <= r;k++)
        {
            if(counted == false && R[j] < L[i])
            {
                inversion += n1-i+1;
                counted = true;
            }
            if(L[i] <= R[j])
            {
                A[k] = L[i++];
            }
            else
            {
                A[k] = R[j++];
                counted = false;
            }

        }
        return inversion;
    }
};
