// class Solution {
// public:
//     vector<int> intersect(vector<int>& nums1, vector<int>& nums2) {
//         sort(nums1.begin(),nums1.end());
//         sort(nums2.begin(),nums2.end());
//
//         vector<int>::iterator it1 = nums1.begin();
//         vector<int>::iterator it2 = nums2.begin();
//         vector<int> ans;
//
//         while(it1 != nums1.end() && it2 != nums2.end())
//         {
//             if(*it1 == *it2)
//             {
//                 ans.push_back(*it1);
//                 it1++;
//                 it2++;
//             }
//             else if(*it1 < *it2)
//                 it1++;
//             else
//                 it2++;
//         }
//         return ans;
//     }
// };



class Solution {

public:
    template <class T>

    void swap(T &a, T& b)
    {
        T temp = a;
        a = b;
        b = temp;
    }

    typedef vector<int>::iterator iter;
    void MyInsertSort(iter first, iter last)
    {
        int len = last-first;
        for(int i = 1, j = 0; i < len; i++)
        {
            int temp = *(first+i);
            for(j = i-1;j >= 0 && temp < *(first+j) ;j--)
            {
                *(first+j+1) = *(first+j);
            }
            *(first+j+1) = temp;
        }
    }

    void MyBubbleSort(iter first, iter last)
    {
        int len = last-first;
        for(int i = 0;i < len; i++)
        {
            for(int j = 0;j < len-1; j++)
            {
                if(*(first+j) > *(first+j+1))
                    swap(*(first+j), *(first+j+1));
            }
        }
    }


    vector<int> intersect(vector<int>& nums1, vector<int>& nums2) {
        MyInsertSort(nums1.begin(),nums1.end());
        MyInsertSort(nums2.begin(),nums2.end());


        vector<int>::iterator it1 = nums1.begin();
        vector<int>::iterator it2 = nums2.begin();
        vector<int> ans;

        for(;it1 != nums1.end();it1++)
        {
            cout << *it1 << "\t";
        }
        cout << endl;

        for(;it2 != nums2.end();it2++)
        {
            cout << *it2 << "\t";
        }


        while(it1 != nums1.end() && it2 != nums2.end())
        {
            if(*it1 == *it2)
            {
                ans.push_back(*it1);
                it1++;
                it2++;
            }
            else if(*it1 < *it2)
                it1++;
            else if(*it1 > *it2)
                it2++;
            else
                cout << "error" << *it1 <<'\t' << *it2 << endl;
        }
        return ans;
    }
};
