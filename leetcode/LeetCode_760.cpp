class Solution {
public:
    vector<int> anagramMappings(vector<int>& A, vector<int>& B) {
        vector<int> ans(A.size());
        for(int i = 0;i < A.size();)
        {
            for(int j = 0;j < B.size() ;j++)
            {
                if(B[j] >= 0 && A[i] == B[j])
                {
                    ans[i++] = j;
                    B[j] = -1;
                }
            }
        }
        return ans;
    }
};
