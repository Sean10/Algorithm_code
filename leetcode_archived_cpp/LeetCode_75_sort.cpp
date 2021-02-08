class Solution {
public:
    template <typename T>
    void Swap(T &a, T &b)
    {
        T temp = a;
        a = b;
        b = temp;
    }

    void ShellSort(vector<int>& nums)
    {
        int len = nums.size();
        for(int gap = len >> 1; gap > 0; gap >>= 1)
        {
            for(int i = gap, j= 0; i < len;++i)
            {
                int temp = nums[i];
                for(j = i - gap; j >= 0 && temp < nums[j] ; j -= gap)
                {
                    nums[j+gap] = nums[j];
                }
                nums[j+gap] = temp;
            }
        }
    }

    void InsertSort(vector<int>& nums)
    {
        for(int i = 1 ,j = 0;i < nums.size(); i++)
        {
            int temp = nums[i];

            for(j = i-1; j >= 0 && temp < nums[j] ; j--)
            {
                nums[j+1] = nums[j];
            }
            nums[j+1] = temp;
        }
    }

    void BubbleSort(vector<int>& nums)
    {
        for(int i = 0;i < nums.size(); i++)
        {
            for(int j = 1;j < nums.size();j++)
            {
                if(nums[j-1] > nums[j])
                    Swap(nums[j-1], nums[j]);
            }
        }
    }

    void BinaryInsertSort(vector<int>& nums)
    {
        int low,mid,high;

        for(int i = 1;i < nums.size(); i++)
        {
            int temp = nums[i];
            low = 0;
            high = i-1;
            while(low <= high)
            {
                mid = (low+high)/2;
                if(nums[mid] > temp)
                    high = mid - 1;
                else
                    low = mid + 1;
            }
            for(int j = i-1; j >= high+1; --j)
                nums[j+1] = nums[j];
            nums[high+1] = temp;

            for(int x = 0;x < nums.size();x++)
                cout << nums[x] << "\t";
            cout << endl;
        }
    }

    void sortColors(vector<int>& nums) {
        //BubbleSort(nums);
        //InsertSort(nums);
        //BinaryInsertSort(nums);
        ShellSort(nums);
    }
};
