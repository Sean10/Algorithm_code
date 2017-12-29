class Solution {
public:
    int findRadius(vector<int>& houses, vector<int>& heaters) {
        qsort(houses,0,houses.size()-1);
        qsort(heaters,0, heaters.size()-1);

        int n = max(houses.size(), heaters.size());
        vector<int> ans(houses.size(), INT_MAX);

        for(int i = 0, j = 0;i < houses.size() && j < heaters.size();)
        {
            if(houses[i] < heaters[j])
            {
                ans[i] = heaters[j]-houses[i];
                i++;
            }else
                j++;
        }

        for(int i = houses.size()-1, j = heaters.size()-1; i >= 0 && j >= 0;)
        {
            if(houses[i] >= heaters[j])
            {
                ans[i] = min(ans[i], houses[i]-heaters[j]);
                i--;
            }else
                j--;
        }

        return *max_element(ans.begin(), ans.end());
    }

    void qsort(vector<int>& V,int left, int right)
    {
        if(left >= right)
            return ;
        int mid = partition(V, left, right);
        qsort(V, left, mid-1);
        qsort(V, mid+1, right);
    }

    int partition(vector<int>& V, int left, int right)
    {
        int temp = V[left];
        while(left < right)
        {
            while(left < right && V[right] > temp)
                right--;
            if(left < right)
                V[left++] = V[right];
            while(left < right && V[left] < temp)
                left++;
            if(left < right)
                V[right--] = V[left];
        }
        V[left] = temp;
        return left;
    }
};
