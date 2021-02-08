class Solution {
public:
    int hIndex(vector<int>& citations) {
        qsort(citations, 0, citations.size()-1);
        int max_index = 0;
        for(int i = 0;i < citations.size();i++)
        {
            if(citations[i] >= i+1)
                max_index = max(max_index, i+1);
        }
        return max_index;
    }
private:
    void qsort(vector<int>& citations, int left, int right)
    {
        if(left > right)
            return ;
        int mid = partition(citations,left,right);
        qsort(citations, left, mid-1);
        qsort(citations, mid+1, right);
    }

    int partition(vector<int>& citations, int left, int right)
    {
        int i = left, j = right;
        int temp = citations[i];
        while(i < j)
        {
            while(i < j && temp > citations[j])
                j--;
            if(i < j)
            {
                citations[i++] = citations[j];
            }

            while(i < j && temp < citations[i])
                i++;
            if(i < j)
                citations[j--] = citations[i];
        }
        citations[i] = temp;
        return i;
    }
};
